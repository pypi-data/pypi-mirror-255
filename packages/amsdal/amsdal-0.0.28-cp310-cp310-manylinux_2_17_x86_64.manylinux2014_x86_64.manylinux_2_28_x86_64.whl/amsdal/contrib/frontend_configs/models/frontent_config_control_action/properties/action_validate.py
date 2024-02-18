from pydantic import field_validator


@field_validator('action', mode='after')  # type: ignore[misc]
@classmethod
def validate_action(cls, v: str) -> str:  # type: ignore[no-untyped-def] # noqa: ARG001
    if not v.startswith('navigate::') and v not in [
        'goPrev',
        'goNext',
        'goNextWithSubmit',
        'submit',
        'submitWithDataLayer',
    ]:
        msg = 'Action must be one of: goPrev, goNext, goNextWithSubmit, submit, submitWithDataLayer, navigate::{string}'
        raise ValueError(msg)

    return v
