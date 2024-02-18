import subprocess
import sys

from copier_example import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "copier_example", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
