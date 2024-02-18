import getpass
import subprocess
from mst.core.usage_logger import LogAPIUsage


class AuthSRV:
    """Interface for AuthSRV credential retrieval."""

    def __init__(self, path: str = ""):
        """Create instance of AuthSRV, optionally setting prefix for authsrv executeables,
        should end in platform specific path separator.

        Args:
            path (str, optional): Prefix for authsrv executeables,
                should end in platform specific path separator. Defaults to "".
        """
        self.authsrv_decrypt = f"{path}authsrv-decrypt"

    def fetch(self, instance: str, owner=getpass.getuser(), user=getpass.getuser()):
        """returns stashed password, "user" defaults to the current userid on unix.
        If running as root, "owner" can be specified.

        Args:
            owner (str): If running as root, "owner" can be specified. Defaults to getpass.getuser().
            user (str): Defaults to the current user.
            instance (str): instance name.

        Raises:
            ValueError: When user is not defined
            ValueError: When instance is not defined

        Returns:
            str: the fetched value from authsrv-decrypt
        """
        LogAPIUsage()

        if owner != getpass.getuser() and getpass.getuser() != "root":
            owner = getpass.getuser()

        if user is None:
            raise ValueError(__name__, "(): user must be defined")

        if instance is None:
            raise ValueError(__name__, "(): instance must be defined")

        return (
            subprocess.check_output([self.authsrv_decrypt, owner, user, instance])
            .decode("utf-8")
            .rstrip("\r\n")
        )
