import os
import platform

from truera.client.errors import SimpleException


class ContextSetupException(SimpleException):
    pass


def get_context_storage_base_path():
    if platform.system().lower() == "windows":
        home_path = os.path.join(
            os.environ["HOMEDRIVE"], os.environ["HOMEPATH"]
        )
        user_profile = os.environ["USERPROFILE"]

        base_dir = None
        if os.path.isdir(home_path):
            base_dir = home_path
        elif os.path.isdir(user_profile):
            base_dir = user_profile
        else:
            print(
                f"Warning: Could not determine base_dir from %HOMEDRIVE%\%HOMEPATH% ({home_path}) or from %USERPROFILE% ({user_profile})."
            )
            print(f"Warning: Trying %SYSTEMDRIVE%:\%HOMEPATH%...")
            base_dir = os.path.join(
                os.environ["SYSTEMDRIVE"], os.environ["HOMEPATH"]
            )
            if not os.path.isdir(base_dir):
                message = f"%SYSTEMDRIVE%\%HOMEPATH% ({base_dir}) does not exist. Please set %USERPROFILE% to a drive that exists."
                print(f"Error: {message}")
                raise ContextSetupException(message)
        return os.path.join(base_dir, "Truera")
    else:
        return os.path.join(os.environ["HOME"], ".truera")