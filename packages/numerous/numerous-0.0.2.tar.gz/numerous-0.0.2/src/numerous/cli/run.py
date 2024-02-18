"""Launches the correct binary for the users OS."""

import os
import platform
import subprocess
import sys
from pathlib import Path


def get_exe_name() -> str:
    system_info = platform.system()
    if system_info == "Linux":
        return "build/cli.linux"
    elif system_info == "Darwin":  # noqa: RET505
        return "build/cli.macos"
    elif os.name == "nt":
        return "build/cli.windows"
    else:
        print("Sorry but", os.name, "is not currently supported :(")  # noqa: T201
        sys.exit(1)


def main() -> None:
    exe_name = get_exe_name()
    exe_path = Path(__file__).parent / exe_name
    subprocess.run([str(exe_path)] + sys.argv[1:], check=False)  # noqa: S603


if __name__ == "__main__":
    main()
