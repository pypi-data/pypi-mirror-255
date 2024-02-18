"""Class to lock a file to prevent concurrent access to it."""

import os
import time
from regscale.core.app.utils.app_utils import check_file_path


class FileLock:
    """Class to lock a file to prevent concurrent access to it"""

    lock_file: str
    lock_scope: str
    skip_lock: bool

    def __init__(
        self, lock_file: str = "results/xdist_lock.txt", skip_lock: bool = False
    ):
        """
        Initialize the FileLock class.
        :param str lock_file: File to lock, defaults to "results/xdist_lock.txt"
        :param str skip_lock: Whether to skip the lock, defaults to False
        """
        self.lock_file: str = lock_file
        self.lock_scope: str = f"{os.getpid()}".ljust(10, ".")
        self.skip_lock = skip_lock
        lock_folder = os.path.dirname(self.lock_file)
        check_file_path(lock_folder, False)

    def __enter__(self) -> "FileLock":
        """
        Enter the context manager.

        :return: The FileLock object
        :rtype: FileLock
        """
        if not self.skip_lock:
            self.acquire_lock()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager.

        :param exc_type:  Exception type
        :param exc_value: Exception value
        :param traceback: Traceback
        :return: None
        """
        if not self.skip_lock:
            self.release_lock()

    def lock_contents(self) -> str:
        """
        Get the contents of the lock file.

        :return: Contents of the lock file as a string
        :rtype: str
        """
        with open(self.lock_file, "r") as lockfile:
            contents = lockfile.read()
        return contents

    def acquire_lock(self) -> None:
        """
        Acquire the lock.

        :return: None
        """
        try:
            while os.path.isfile(self.lock_file):
                # Another process is holding the lock. Waiting to acquire...
                time.sleep(0.1)
            # Create the lock file with the pid inside
            with open(self.lock_file, "w") as lockfile:
                lockfile.write(f"{self.lock_scope}")
            # Read the lock file to make sure the contents is ours
            with open(self.lock_file, "r") as lockfile:
                contents = lockfile.read()
            # If the contents is not ours, race condition -> back to square one
            if contents != f"{self.lock_scope}":
                self.acquire_lock()
        except Exception:
            self.acquire_lock()

    def release_lock(self) -> None:
        """
        Release the lock.

        :return: None
        """
        if os.path.isfile(self.lock_file):
            with open(self.lock_file, "r") as lockfile:
                scope = str(lockfile.read().strip())

            if scope == str(self.lock_scope):
                os.remove(self.lock_file)  # Lock released
            else:
                pass  # Lock can only be released by {self.lock_scope}
