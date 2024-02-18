@property  # type: ignore[misc]
def mimetype(self) -> str | None:  # type: ignore[no-untyped-def]
    import mimetypes

    return mimetypes.guess_type(self.filename)[0]
