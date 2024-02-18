def pre_update(self):  # type: ignore[no-untyped-def]
    self.size = len(self.data or b'')
