import decimal
import json
import os
from collections import OrderedDict
from functools import lru_cache, reduce
from typing import Any, Dict, List, Optional, Pattern, Tuple, TypeVar, Union

from lumigo_core.configuration import (
    MASK_ALL_REGEX,
    CoreConfiguration,
    create_regex_from_list,
)
from lumigo_core.logger import get_logger
from lumigo_core.lumigo_utils import aws_dump

MANUAL_TRACES_KEY = "manualTraces"
EXECUTION_TAGS_KEY = "lumigo_execution_tags_no_scrub"
SKIP_SCRUBBING_KEYS = [EXECUTION_TAGS_KEY, MANUAL_TRACES_KEY]
OMITTING_KEYS_REGEXES = [
    ".*pass.*",
    ".*key.*",
    ".*secret.*",
    ".*credential.*",
    "SessionToken",
    "x-amz-security-token",
    "Signature",
    "Authorization",
]
LUMIGO_SECRET_MASKING_REGEX_BACKWARD_COMP = (
    "LUMIGO_BLACKLIST_REGEX"  # pragma: allowlist secret
)
LUMIGO_SECRET_MASKING_REGEX = "LUMIGO_SECRET_MASKING_REGEX"  # pragma: allowlist secret
MASKED_SECRET = "****"
TRUNCATE_SUFFIX = "...[too long]"

Container = TypeVar("Container", Dict[Any, Any], List[Any])


@lru_cache(maxsize=1)
def get_omitting_regex() -> Optional[Pattern[str]]:
    if LUMIGO_SECRET_MASKING_REGEX in os.environ:
        given_regexes = json.loads(os.environ[LUMIGO_SECRET_MASKING_REGEX])
    elif LUMIGO_SECRET_MASKING_REGEX_BACKWARD_COMP in os.environ:
        given_regexes = json.loads(
            os.environ[LUMIGO_SECRET_MASKING_REGEX_BACKWARD_COMP]
        )
    else:
        given_regexes = OMITTING_KEYS_REGEXES
    if not given_regexes:
        return None
    return create_regex_from_list(given_regexes)


def _recursive_omitting(
    prev_result: Tuple[Container, int],
    item: Tuple[Optional[str], Any],
    regex: Optional[Pattern[str]],
    enforce_jsonify: bool,
    decimal_safe: bool = False,
    omit_skip_path: Optional[List[str]] = None,
) -> Tuple[Container, int]:
    """
    This function omitting keys until the given max_size.
    This function should be used in a reduce iteration over dict.items().

    :param prev_result: the reduce result until now: the current dict and the remaining space
    :param item: the next yield from the iterator dict.items()
    :param regex: the regex of the keys that we should omit
    :param enforce_jsonify: should we abort if the object can not be jsonify.
    :param decimal_safe: should we accept decimal values
    :return: the intermediate result, after adding the current item (recursively).
    """
    key, value = item
    d, free_space = prev_result
    if free_space < 0:
        return d, free_space
    should_skip_key = False
    if isinstance(d, dict) and omit_skip_path:
        should_skip_key = omit_skip_path[0] == key
        omit_skip_path = omit_skip_path[1:] if should_skip_key else None
    if key in SKIP_SCRUBBING_KEYS:
        new_value = value
        free_space -= (
            len(value) if isinstance(value, str) else len(aws_dump({key: value}))
        )
    elif isinstance(key, str) and regex and regex.match(key) and not should_skip_key:
        new_value = "****"
        free_space -= 4
    elif isinstance(value, (dict, OrderedDict)):
        new_value, free_space = reduce(
            lambda p, i: _recursive_omitting(
                p, i, regex, enforce_jsonify, omit_skip_path=omit_skip_path
            ),
            value.items(),
            ({}, free_space),
        )
    elif isinstance(value, decimal.Decimal):
        new_value = float(value)
        free_space -= 5
    elif isinstance(value, list):
        new_value, free_space = reduce(
            lambda p, i: _recursive_omitting(
                p, (None, i), regex, enforce_jsonify, omit_skip_path=omit_skip_path
            ),
            value,
            ([], free_space),
        )
    elif isinstance(value, str):
        new_value = value
        free_space -= len(new_value)
    else:
        try:
            free_space -= len(aws_dump({key: value}, decimal_safe=decimal_safe))
            new_value = value
        except TypeError:
            if enforce_jsonify:
                raise
            new_value = str(value)
            free_space -= len(new_value)
    if isinstance(d, list):
        d.append(new_value)
    else:
        d[key] = new_value
    return d, free_space


def omit_keys(
    value: Dict,  # type: ignore[type-arg]
    in_max_size: Optional[int] = None,
    regexes: Optional[Pattern[str]] = None,
    enforce_jsonify: bool = False,
    decimal_safe: bool = False,
    omit_skip_path: Optional[List[str]] = None,
) -> Tuple[Dict, bool]:  # type: ignore[type-arg]
    """
    This function omit problematic keys from the given value.
    We do so in the following cases:
    * if the value is dictionary, then we omit values by keys (recursively)
    """
    if CoreConfiguration.should_scrub_known_services:
        omit_skip_path = None
    regexes = regexes or get_omitting_regex()
    max_size = in_max_size or CoreConfiguration.max_entry_size
    omitted, size = reduce(  # type: ignore
        lambda p, i: _recursive_omitting(
            prev_result=p,
            item=i,
            regex=regexes,
            enforce_jsonify=enforce_jsonify,
            decimal_safe=decimal_safe,
            omit_skip_path=omit_skip_path,
        ),
        value.items(),
        ({}, max_size),
    )
    return omitted, size < 0


def lumigo_dumps_with_context(
    context: str,
    d: Union[bytes, str, dict, OrderedDict, list, None],  # type: ignore[type-arg]
    max_size: Optional[int] = None,
    enforce_jsonify: bool = False,
    decimal_safe: bool = False,
    omit_skip_path: Optional[List[str]] = None,
) -> str:
    """
    This function is a wrapper for lumigo_dumps.
    It adds the context to the dumped value.
    """
    regexes: Optional[Pattern[str]] = None
    if context == "environment":
        regexes = CoreConfiguration.secret_masking_regex_environment
    elif context == "requestBody":
        regexes = CoreConfiguration.secret_masking_regex_http_request_bodies
    elif context == "requestHeaders":
        regexes = CoreConfiguration.secret_masking_regex_http_request_headers
    elif context == "responseBody":
        regexes = CoreConfiguration.secret_masking_regex_http_response_bodies
    elif context == "responseHeaders":
        regexes = CoreConfiguration.secret_masking_regex_http_response_headers
    else:
        get_logger().warning("Unknown context for shallowMask", context)

    if regexes == MASK_ALL_REGEX:
        return MASKED_SECRET

    return lumigo_dumps(
        d,
        max_size=max_size,
        regexes=regexes,
        enforce_jsonify=enforce_jsonify,
        decimal_safe=decimal_safe,
        omit_skip_path=omit_skip_path,
    )


def lumigo_dumps(
    d: Union[bytes, str, dict, OrderedDict, list, None],  # type: ignore[type-arg]
    max_size: Optional[int] = None,
    regexes: Optional[Pattern[str]] = None,
    enforce_jsonify: bool = False,
    decimal_safe: bool = False,
    omit_skip_path: Optional[List[str]] = None,
) -> str:
    regexes = regexes or get_omitting_regex()
    max_size = (
        max_size if max_size is not None else CoreConfiguration.get_max_entry_size()
    )
    is_truncated = False

    if isinstance(d, bytes):
        try:
            d = d.decode()
        except Exception:
            d = str(d)
    if isinstance(d, str) and d.startswith("{"):
        try:
            d = json.loads(d)
        except Exception:
            pass
    if isinstance(d, dict):
        d, is_truncated = omit_keys(
            d,
            max_size,
            regexes,
            enforce_jsonify,
            decimal_safe=decimal_safe,
            omit_skip_path=omit_skip_path,
        )
    elif isinstance(d, list):
        size = 0
        organs = []
        for a in d:
            organs.append(
                lumigo_dumps(
                    a, max_size, regexes, enforce_jsonify, omit_skip_path=omit_skip_path
                )
            )
            size += len(organs[-1])
            if size > max_size:
                break
        return "[" + ", ".join(organs) + "]"

    try:
        if isinstance(d, str) and d.endswith(TRUNCATE_SUFFIX):
            return d
        retval = aws_dump(d, decimal_safe=decimal_safe)
    except TypeError:
        if enforce_jsonify:
            raise
        retval = str(d)
    return (
        (retval[:max_size] + TRUNCATE_SUFFIX)
        if len(retval) >= max_size or is_truncated
        else retval
    )
