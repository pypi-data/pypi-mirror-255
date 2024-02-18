import os
import os.path
import re
import subprocess
import sys

import click

# Install / upgrade python in the global environment
# Yes, I know, we must be already running python, but... here we can upgrade it or install
# new versions, etc.

major, minor = sys.version_info[:2]
this_version = f"{major}.{minor}"


def validate_version(version):
    parts = version.split(".")
    if len(parts) < 2 or len(parts) > 3:
        raise ValueError(f"Invalid version {version}")
    for part in parts:
        if not part.isdigit():
            raise ValueError(f"Invalid version {version}")


def get_major(version):
    return ".".join(version.split(".")[:2])


def install_python(version="3.12"):
    """Install python in the global environment."""
    validate_version(version)

    # check if it is already installed
    if is_installed(version):
        print(f"Python {version} already installed")
        return

    installdir = get_install_location(version)

    # install via winget
    print(f"Installing python {version}...")
    subprocess.run(
        [
            "winget",
            "install",
            "--accept-source-agreements",
            "--accept-package-agreements",
            "--scope",
            "machine",
            "-e",
            "--id",
            f"Python.Python.{major}",
            "--location",
            installdir,
        ],
        check=True,
    )
    print("Python installed")


def get_install_location(version):
    """Get the installation location of python version."""
    # create something like C:\Python312
    major = get_major(version)
    program_files = os.environ["ProgramFiles"]
    drive = os.path.splitdrive(program_files)[0]
    suffix = "".join(major.split("."))
    installdir = os.path.join(drive, "\\Python" + suffix)
    return installdir


def upgrade_python(
    version=None, silent=False, interactive=False, install=False, self_upgrade=False
):
    """Upgrade python in the global environment."""
    if version is None:
        version = get_version()
    major = get_major(version)

    if major == this_version and not self_upgrade:
        print(
            f"Cannot upgrade python {version} from itself, use --self-upgrade to create a bat file to do it."
        )
        return False

    # check if it is already installed
    if not is_installed(version):
        if install:
            return install_python(version, silent=silent, interactive=interactive)
        else:
            raise ValueError(f"Python {version} is not installed")

    # winget upgrade is not working, it won't accept the machine scope and will put the new version
    # in the default location.  Instead, use install, which will upgrade if it can, but we must
    # use 'force' to force winget to download the installer.

    # get current install dir
    installdir = get_install_dir(major)

    # install via winget
    cmd = [
        "winget",
        "install",
        "--force",  # force download of installer
        "--accept-source-agreements",
        "--accept-package-agreements",
        "-e",
        "--id",
        f"Python.Python.{major}",
        "--location",
        installdir,
        "--scope",
        "machine",
    ]
    if silent:
        cmd.append("--silent")
    if interactive:
        cmd.append("--interactive")

    if major != this_version:
        print(f"Upgrading python {version}...")
        subprocess.run(cmd, check=True)
        print("Python upgraded")
    else:
        print(f"Creating bat file to upgrade python {version}...")
        filename = "upgrade_python.bat"
        with open(filename, "w") as f:
            f.write(" ".join(cmd))
        print(f"run '{filename}' to upgrade python.")
    return True


def get_version(major=None):
    """Get the version of python installed in the global environment."""
    if major is None:
        cmd = ["py", "--version"]
    else:
        cmd = ["py", f"-{major}", "--version"]
    out = subprocess.run(cmd, capture_output=True)
    if out.returncode != 0:
        return None  # not installed
    return out.stdout.decode().strip().split()[1]


def is_installed(version):
    """Check if python version is installed"""

    major = get_major(version)
    out = subprocess.run(["py", f"-{major}", "--version"], capture_output=True)
    return out.returncode == 0


def get_install_dir(version):
    """Get the installation directory of python version."""
    major = get_major(version)
    out = subprocess.run(["py", "--list-paths"], capture_output=True, check=True)
    for line in out.stdout.decode().splitlines():
        prefix, path = line.rsplit(None, 1)
        match = re.search(r"-V:(\d+\.\d+)", prefix)
        if match:
            version = match.group(1)
            if version == major:
                location = os.path.normpath(os.path.dirname(path))
                return location


@click.group()
@click.option("--interactive", is_flag=True, help="Requests interactive mode.")
@click.option("--silent", is_flag=True, help="Requests silent mode.")
@click.pass_context
def python(ctx, interactive, silent):
    """Manage python in the global environment."""
    ctx.ensure_object(dict)
    ctx.obj["interactive"] = interactive
    ctx.obj["silent"] = silent


@python.command()
@click.option("--version", "-v", default="3.12", help="Version to install.")
@click.pass_context
def install(ctx, version):
    """Install python in the global environment."""
    install_python(
        version, interactive=ctx.obj["interactive"], silent=ctx.obj["silent"]
    )


@python.command()
@click.option("--version", "-v", type=str, default=None, help="Version to install.")
@click.option(
    "--self-upgrade",
    is_flag=True,
    help="Create a bat file to upgrade python from itself.",
)
@click.pass_context
def upgrade(ctx, version, self_upgrade):
    """Upgrade python in the global environment."""
    upgrade_python(
        version,
        interactive=ctx.obj["interactive"],
        silent=ctx.obj["silent"],
        self_upgrade=self_upgrade,
    )
