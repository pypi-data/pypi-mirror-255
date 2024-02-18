from pathlib import Path
from typing import BinaryIO


def to_file(self, file_or_path: Path | BinaryIO) -> None:  # type: ignore[no-untyped-def]
    if isinstance(file_or_path, Path):
        if file_or_path.is_dir():
            file_or_path = file_or_path / self.name
        file_or_path.write_bytes(self.data)  # type: ignore[union-attr]
    else:
        file_or_path.write(self.data)
        file_or_path.seek(0)
