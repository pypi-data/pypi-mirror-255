import decimal
import hashlib
import json
import time
from typing import Any, Dict


def get_current_ms_time() -> int:
    """
    :return: the current time in milliseconds
    """
    return int(time.time() * 1000)


class DecimalEncoder(json.JSONEncoder):
    # copied from python's runtime: runtime/lambda_runtime_marshaller.py:7-11
    def default(self, o: Any) -> Any:
        if isinstance(o, decimal.Decimal):
            return float(o)
        raise TypeError(
            f"Object of type {o.__class__.__name__} is not JSON serializable"
        )


def aws_dump(d: Any, decimal_safe: bool = False, **kwargs) -> str:  # type: ignore[no-untyped-def]
    if decimal_safe:
        return json.dumps(d, cls=DecimalEncoder, **kwargs)
    return json.dumps(d, **kwargs)


def md5hash(d: Dict[Any, Any]) -> str:
    h = hashlib.md5()
    h.update(aws_dump(d, sort_keys=True).encode())
    return h.hexdigest()
