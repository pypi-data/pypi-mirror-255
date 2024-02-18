import json
import os
import re
from typing import List, Optional, Pattern

from lumigo_core.logger import get_logger

MASKING_REGEX_HTTP_REQUEST_BODIES = "LUMIGO_SECRET_MASKING_REGEX_HTTP_REQUEST_BODIES"
MASKING_REGEX_HTTP_REQUEST_HEADERS = "LUMIGO_SECRET_MASKING_REGEX_HTTP_REQUEST_HEADERS"
MASKING_REGEX_HTTP_RESPONSE_BODIES = "LUMIGO_SECRET_MASKING_REGEX_HTTP_RESPONSE_BODIES"
MASKING_REGEX_HTTP_RESPONSE_HEADERS = (
    "LUMIGO_SECRET_MASKING_REGEX_HTTP_RESPONSE_HEADERS"
)
MASKING_REGEX_HTTP_QUERY_PARAMS = "LUMIGO_SECRET_MASKING_REGEX_HTTP_QUERY_PARAMS"
MASKING_REGEX_ENVIRONMENT = "LUMIGO_SECRET_MASKING_REGEX_ENVIRONMENT"
MASKING_ALL_MAGIC_STRING = "all"
MASK_ALL_REGEX = re.compile(r".*", re.IGNORECASE)

DEFAULT_MAX_ENTRY_SIZE = 2048


def create_regex_from_list(regexes: Optional[List[str]]) -> Optional[Pattern[str]]:
    """
    For performance - we create a single regex from all the regexes.
    """
    if not regexes:
        return None
    return re.compile(fr"({'|'.join(regexes)})", re.IGNORECASE)


def parse_regex_from_env(env_key: str) -> Optional[Pattern[str]]:
    if env_key in os.environ:
        if os.environ[env_key].lower() == MASKING_ALL_MAGIC_STRING:
            return MASK_ALL_REGEX
        try:
            regexes = json.loads(os.environ[env_key])
            return create_regex_from_list(regexes)
        except Exception:
            get_logger().critical(
                f"Could not parse the specified scrubber in {env_key}, shutting down the tracer."
            )
            CoreConfiguration.should_report = False
    return None


def get_config_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, default))
    except ValueError:
        get_logger().error(f"Invalid value for config {key}, using default")
        return default


class CoreConfiguration:
    chained_services_max_depth: int = get_config_int(
        "LUMIGO_CHAINED_SERVICES_MAX_DEPTH", 3
    )
    chained_services_max_width: int = get_config_int(
        "LUMIGO_CHAINED_SERVICES_MAX_WIDTH", 5
    )
    should_report: bool = True
    should_scrub_known_services = (
        os.environ.get("LUMIGO_SCRUB_KNOWN_SERVICES") == "true"
    )
    secret_masking_regex_http_request_bodies = parse_regex_from_env(
        MASKING_REGEX_HTTP_REQUEST_BODIES
    )
    secret_masking_regex_http_request_headers = parse_regex_from_env(
        MASKING_REGEX_HTTP_REQUEST_HEADERS
    )
    secret_masking_regex_http_response_bodies = parse_regex_from_env(
        MASKING_REGEX_HTTP_RESPONSE_BODIES
    )
    secret_masking_regex_http_response_headers = parse_regex_from_env(
        MASKING_REGEX_HTTP_RESPONSE_HEADERS
    )
    secret_masking_regex_http_query_params = parse_regex_from_env(
        MASKING_REGEX_HTTP_QUERY_PARAMS
    )
    secret_masking_regex_environment = parse_regex_from_env(MASKING_REGEX_ENVIRONMENT)
    max_entry_size = get_config_int("LUMIGO_MAX_ENTRY_SIZE", DEFAULT_MAX_ENTRY_SIZE)
    max_entry_size_on_error = get_config_int(
        "LUMIGO_MAX_ENTRY_SIZE_ON_ERROR", max_entry_size * 2
    )

    @staticmethod
    def get_max_entry_size(has_error: bool = False) -> int:
        if has_error:
            return CoreConfiguration.max_entry_size_on_error
        return CoreConfiguration.max_entry_size
