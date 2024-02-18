import base64

from pydantic import field_validator


@field_validator('data')  # type: ignore[misc]
@classmethod
def data_base64_decode(cls, v: bytes) -> bytes:  # type: ignore[no-untyped-def]  # noqa: ARG001
    is_base64: bool = False

    try:
        is_base64 = base64.b64encode(base64.b64decode(v)) == v
    except Exception:
        ...

    if is_base64:
        return base64.b64decode(v)

    return v
