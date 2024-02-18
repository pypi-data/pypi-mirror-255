"""Library defining the interface to the generative firewall."""
import atexit
import time
from typing import Any, Iterable, List, Optional

from urllib3.util import Retry

from rime_sdk.authenticator import Authenticator
from rime_sdk.client import RETRY_HTTP_STATUS
from rime_sdk.internal.rest_error_handler import RESTErrorHandler
from rime_sdk.swagger.swagger_client import (
    ApiClient,
    Configuration,
    FirewallApi,
    FirewallInstanceManagerApi,
    GenerativefirewallCreateFirewallInstanceRequest,
    GenerativefirewallCreateFirewallInstanceResponse,
    GenerativefirewallFirewallInstanceInfo,
    GenerativefirewallFirewallInstanceStatus,
    GenerativefirewallFirewallRuleConfig,
    GenerativefirewallGetFirewallEffectiveConfigResponse,
    GenerativefirewallGetFirewallInstanceResponse,
    GenerativefirewallListFirewallInstancesResponse,
    GenerativefirewallValidateRequest,
    RimeUUID,
    ValidateRequestInput,
    ValidateRequestOutput,
)
from rime_sdk.swagger.swagger_client.models.rime_language import RimeLanguage

_DEFAULT_CHANNEL_TIMEOUT = 60.0


VALID_LANGUAGES = [
    RimeLanguage.EN,
    RimeLanguage.JA,
]


def _get_firewall_instance_info(
    instance_manager_client: FirewallInstanceManagerApi, firewall_instance_id: str
) -> GenerativefirewallFirewallInstanceInfo:
    with RESTErrorHandler():
        res: GenerativefirewallGetFirewallInstanceResponse = (
            instance_manager_client.firewall_instance_manager_get_firewall_instance(
                firewall_instance_id
            )
        )
        fw_instance: GenerativefirewallFirewallInstanceInfo = res.firewall_instance
    return fw_instance


class FirewallInstance:
    """An interface to a single instance of the firewall running on a cluster.

    Each FirewallInstance has its own rule configuration and can be accessed
    by its unique ID.
    This allows users to customize the behavior of the firewall for different
    use cases.
    Note: FirewallInstance should not be instantiated directly, but instead
    instantiated through methods of the FirewallClient.

    Args:
        firewall_instance_id: str
            The unique ID of the FirewallInstance.
        api_client: ApiClient
            API client for interacting with the cluster.
    """

    def __init__(self, firewall_instance_id: str, api_client: ApiClient) -> None:
        """Initialize a new FirewallInstance."""
        self._firewall_instance_id = firewall_instance_id
        self._api_client = api_client
        self._firewall_client = FirewallApi(self._api_client)
        self._instance_manager_client = FirewallInstanceManagerApi(self._api_client)

        # The rule config for a single FirewallInstance is immutable, so we can
        # fetch it and save it on the class.
        # This has the added benefit of confirming that the customer has
        # instantiated with FirewallInstance class correctly.
        fw_instance = _get_firewall_instance_info(
            self._instance_manager_client, self._firewall_instance_id
        )
        conf: GenerativefirewallFirewallRuleConfig = fw_instance.config
        self._rule_config = conf.to_dict() if conf is not None else {}

    def validate(
        self,
        user_input_text: Optional[str] = None,
        output_text: Optional[str] = None,
        contexts: Optional[List[str]] = None,
    ) -> dict:
        """Validate model input and/or output text."""
        if user_input_text is None and output_text is None and contexts is None:
            raise ValueError(
                "Must provide either input text, output text, or context documents to validate."
            )

        body = GenerativefirewallValidateRequest(
            input=ValidateRequestInput(
                user_input_text=user_input_text, contexts=contexts
            ),
            output=ValidateRequestOutput(output_text=output_text),
        )
        with RESTErrorHandler():
            response = self._firewall_client.firewall_validate2(
                body=body, firewall_instance_id_uuid=self.firewall_instance_id
            )
        return response.to_dict()

    def get_effective_config(self) -> dict:
        """Get the effective configuration for the FirewallInstance.

        This effective configuration has default values filled in and shows what
        is actually being used at runtime.
        """
        with RESTErrorHandler():
            res: GenerativefirewallGetFirewallEffectiveConfigResponse = (
                self._firewall_client.firewall_get_firewall_effective_config2(
                    firewall_instance_id_uuid=self.firewall_instance_id
                )
            )
        if res.config is None:
            return {}
        return res.config.to_dict()

    def block_until_ready(
        self,
        verbose: bool = True,
        timeout_sec: float = 180.0,
        poll_rate_sec: float = 5.0,
    ) -> None:
        """Block until ready blocks until the FirewallInstance is ready.

        Raises:
            TimeoutError if the FirewallInstance is not ready by the deadline
            set through `timeout_sec`.
        """
        start_time = time.time()
        if verbose:
            print(
                "Waiting until FirewallInstance {} is ready with timeout {}s".format(
                    self.firewall_instance_id,
                    timeout_sec,
                )
            )
        while True:
            status = self.status

            # Get the total time the caller has been waiting and print it out.
            cur_time = time.time()
            elapsed_time = cur_time - start_time
            if verbose:
                minute, second = divmod(elapsed_time, 60)
                print(
                    "\rStatus: {}, Time Elapsed: {:02}:{:05.2f}".format(
                        status,
                        int(minute),
                        second,
                    ),
                    end="",
                )

            # Either the firewall reaches the ready status or we are ready to
            # time out.
            if (
                status == GenerativefirewallFirewallInstanceStatus.READY
                or elapsed_time >= timeout_sec
            ):
                break

            time.sleep(poll_rate_sec)

        if verbose:
            # Print an extra line because the status has a carriage return.
            print()

        if status != GenerativefirewallFirewallInstanceStatus.READY:
            raise TimeoutError(
                f"FirewallInstance did not reach status READY by the timeout {timeout_sec}s"
            )

    @property
    def rule_config(self) -> dict:
        """Access the rule config of the FirewallInstance.

        This config is immutable after it is created.
        """
        return self._rule_config

    @property
    def firewall_instance_id(self) -> str:
        """Access the UUID of the FirewallInstance."""
        return self._firewall_instance_id

    @property
    def status(self) -> str:
        """Access the current status of the FirewallInstance."""
        fw_instance = _get_firewall_instance_info(
            self._instance_manager_client, self._firewall_instance_id
        )
        return fw_instance.deployment_status


class FirewallClient:
    """An interface to connect to FirewallInstances on a firewall cluster.

    Create a firewall instance by specifying the rule configuration.
    It will take anywhere from a few seconds to a few minutes to spin up, but
    once it is ready, it can respond to validation requests with the custom
    configuration.
    A single firewall cluster can have many firewall instances.
    They are independent from each other.

    Args:
        domain: str
            The base domain/address of the firewall.
        api_key: str
            The API key used to authenticate to the firewall.
        auth_token: str
            The Auth Token used to authenticate to backend services. Optional.
        channel_timeout: float
            The amount of time in seconds to wait for responses from the firewall.
    """

    def __init__(
        self,
        domain: str,
        api_key: str = "",
        auth_token: str = "",
        channel_timeout: float = _DEFAULT_CHANNEL_TIMEOUT,
    ):
        """Create a new Client connected to the services available at `domain`."""
        configuration = Configuration()
        configuration.api_key["X-Firewall-Api-Key"] = api_key
        configuration.api_key["X-Firewall-Auth-Token"] = auth_token
        if domain.endswith("/"):
            domain = domain[:-1]
        if not domain.startswith("https://") and not domain.startswith("http://"):
            domain = "https://" + domain
        configuration.host = domain
        self._api_client = ApiClient(configuration)
        # Prevent race condition in pool.close() triggered by swagger generated code
        atexit.register(self._api_client.pool.close)
        # Sets the timeout and hardcoded retries parameter for the api client.
        self._api_client.rest_client.pool_manager.connection_pool_kw[
            "timeout"
        ] = channel_timeout
        self._api_client.rest_client.pool_manager.connection_pool_kw["retries"] = Retry(
            total=3, status_forcelist=RETRY_HTTP_STATUS
        )
        self._instance_manager_client = FirewallInstanceManagerApi(self._api_client)

    def login(self, email: str, system_account: bool = False) -> None:
        """Login to obtain an auth token.

        Args:
            email: str
                The user's email address that is used to authenticate.

            system_account: bool
                This flag specifies whether it is for a system account token or not.

        Example:
             .. code-block:: python

                firewall.login("dev@robustintelligence.com", True)
        """
        authenticator = Authenticator()
        authenticator.auth(self._api_client.configuration.host, email, system_account)
        with open("./token.txt", "r+") as file1:
            self._api_client.configuration.api_key[
                "X-Firewall-Auth-Token"
            ] = file1.read()

    def list_firewall_instances(self) -> Iterable[FirewallInstance]:
        """List the FirewallInstances for the given cluster."""
        with RESTErrorHandler():
            res: GenerativefirewallListFirewallInstancesResponse = (
                self._instance_manager_client.firewall_instance_manager_list_firewall_instances()
            )
            firewall_instances: List[
                GenerativefirewallFirewallInstanceInfo
            ] = res.firewall_instances
            for r in firewall_instances:
                id: RimeUUID = r.firewall_instance_id
                yield FirewallInstance(id.uuid, self._api_client)

    def create_firewall_instance(
        self,
        rule_config: dict,
        block_until_ready: bool = True,
        block_until_ready_verbose: Optional[bool] = None,
        block_until_ready_timeout_sec: Optional[float] = None,
        block_until_ready_poll_rate_sec: Optional[float] = None,
    ) -> FirewallInstance:
        """Create a FirewallInstance with the specified rule configuration.

        This method blocks until the FirewallInstance is ready.

        Args:
            rule_config: dict
                Dictionary containing the rule config to customize the behavior
                of the FirewallInstance.

            block_until_ready: bool = True
                Whether to block until the FirewallInstance is ready.

            block_until_ready_verbose: Optional[bool] = None
                Whether to print out information while waiting for the FirewallInstance to come up.

            block_until_ready_timeout_sec: Optional[float] = None
                How many seconds to wait until the FirewallInstance comes up before timing out.

            block_until_ready_poll_rate_sec: Optional[float] = None
                How often to poll the FirewallInstance status.

        Returns:
            FirewallInstance that is ready to accept validation requests.

        Raises:
            TimeoutError if the FirewallInstance is not ready by the deadline
            set through `timeout_sec`.
        """
        _config = rule_config.copy()
        language = _config.pop("language", None)
        if language is not None and language not in VALID_LANGUAGES:
            raise ValueError(
                f"Provided language {language} is invalid, please choose one of the "
                f"following values {VALID_LANGUAGES}"
            )

        individual_rules_config = _config.pop("individual_rules_config", None)
        selected_rules = _config.pop("selected_rules", None)
        if _config:
            raise ValueError(
                f"Found unexpected keys in firewall_config: {list(_config.keys())}"
            )
        final_conf = GenerativefirewallFirewallRuleConfig(
            individual_rules_config=individual_rules_config,
            selected_rules=selected_rules,
            language=language,
        )
        req = GenerativefirewallCreateFirewallInstanceRequest(config=final_conf)
        with RESTErrorHandler():
            res: GenerativefirewallCreateFirewallInstanceResponse = self._instance_manager_client.firewall_instance_manager_create_firewall_instance(
                req
            )
        id: RimeUUID = res.firewall_instance_id
        fw = FirewallInstance(id.uuid, self._api_client)

        if block_until_ready:
            # Forward keyword arguments to the FirewallInstance.block_until_ready call.
            block_until_ready_kwargs: dict[str, Any] = {}
            if block_until_ready_verbose:
                block_until_ready_kwargs["verbose"] = block_until_ready_verbose
            if block_until_ready_timeout_sec:
                block_until_ready_kwargs["timeout_sec"] = block_until_ready_timeout_sec
            if block_until_ready_poll_rate_sec:
                block_until_ready_kwargs[
                    "poll_rate_sec"
                ] = block_until_ready_poll_rate_sec
            fw.block_until_ready(**block_until_ready_kwargs)

        return fw

    def get_firewall_instance(self, firewall_instance_id: str) -> FirewallInstance:
        """Get a FirewallInstance from the cluster.

        Args:
            firewall_instance_id: str
                The UUID string of the FirewallInstance to retrieve.

        Returns:
            FirewallInstance:
                A firewall instance on which to perform validation.

        """
        return FirewallInstance(
            firewall_instance_id=firewall_instance_id, api_client=self._api_client
        )

    def delete_firewall_instance(self, firewall_instance_id: str) -> None:
        """Delete a FirewallInstance from the cluster.

        Careful when deleting a FirewallInstance: in-flight validation traffic
        will be interrupted.

        Args:
            firewall_instance_id: str
                The UUID string of the FirewallInstance to hard delete.
        """
        with RESTErrorHandler():
            self._instance_manager_client.firewall_instance_manager_delete_firewall_instance(
                firewall_instance_id
            )
