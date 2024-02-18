def pre_create(self) -> None:  # type: ignore[no-untyped-def]
    self.size = len(self.data or b'')
