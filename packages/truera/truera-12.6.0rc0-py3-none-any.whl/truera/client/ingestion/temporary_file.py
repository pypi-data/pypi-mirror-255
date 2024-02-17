import os
import tempfile
from typing import Optional


class TemporaryFile:
    """Class to serve as a replacement for tempfile.NamedTemporaryFile

    tempfile.NamedTemporaryFile has known issues with Windows NT
    """

    def __init__(
        self,
        mode: Optional[str] = "w+b",
        suffix: Optional[str] = None,
        delete: Optional[bool] = True
    ):
        self._mode = mode
        self._suffix = suffix
        self._delete = delete

        # In some scenarios, we cannot use NamedTemporaryFile
        # directly as it doesn't allow second open on Windows NT.
        # So we use NamedTemporaryFile to just create a name for us
        # and let it delete the file, but use the name later.
        with tempfile.NamedTemporaryFile(mode="w+") as file:
            self.name = file.name
            if self._suffix:
                self.name += self._suffix

    def __enter__(self):
        # Exclusive creation of file
        open(self.name, "x").close()
        # Open file in given mode
        self._tempfile = open(self.name, self._mode)
        return self._tempfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._tempfile.close()
        if self._delete:
            os.remove(self.name)
