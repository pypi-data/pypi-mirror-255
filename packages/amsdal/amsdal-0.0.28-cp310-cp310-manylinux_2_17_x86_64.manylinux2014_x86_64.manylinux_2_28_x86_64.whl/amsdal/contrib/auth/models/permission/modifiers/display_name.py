@property  # type: ignore[misc]
def display_name(self) -> str:  # type: ignore[no-untyped-def]
    return f'{self.model}:{self.action}'
