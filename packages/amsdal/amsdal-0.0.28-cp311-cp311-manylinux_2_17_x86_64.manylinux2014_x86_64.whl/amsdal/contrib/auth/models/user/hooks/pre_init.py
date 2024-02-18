from typing import Any


def pre_init(self, *, is_new_object: bool, kwargs: dict[str, Any]) -> None:  # type: ignore[no-untyped-def]  # noqa: ARG001
    import bcrypt

    from amsdal.contrib.auth.errors import UserCreationError

    email = kwargs.get('email', None)
    password = kwargs.get('password', None)

    if email is None or email == '':
        msg = "Email can't be empty"
        raise UserCreationError(msg)

    if password is None or password == '':
        msg = "Password can't be empty"
        raise UserCreationError(msg)

    kwargs['email'] = email.lower()

    if is_new_object and '_metadata' not in kwargs:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        kwargs['password'] = hashed_password
        kwargs['_object_id'] = email.lower()
