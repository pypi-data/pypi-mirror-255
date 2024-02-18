# stuff to install visual studio
import os.path
import subprocess

import click
import requests
from click import echo

bootstrapper = "https://aka.ms/vs/17/release/vs_community.exe"

install_args = """\
--add Microsoft.VisualStudio.Workload.NativeGame --includeRecommended
--add Microsoft.Net.Component.4.6.2.TargetingPack
--add Microsoft.NetCore.Component.Runtime.6.0
--add Microsoft.Net.Component.4.8.SDK
--add Microsoft.Net.ComponentGroup.4.8.DeveloperTools
--add Microsoft.Component.MSBuild
--add Microsoft.VisualStudio.Component.NuGet
--add Microsoft.NetCore.Component.SDK
--wait --passive --norestart
"""
install_args = " ".join(install_args.split())

update_args = """\
modify --channelid VisualStudio.17.Release --productid Microsoft.VisualStudio.Product.Community
--add Microsoft.VisualStudio.Workload.NativeGame --includeRecommended
--add Microsoft.Net.Component.4.6.2.TargetingPack
--add Microsoft.NetCore.Component.Runtime.6.0
--add Microsoft.Net.Component.4.8.SDK
--add Microsoft.Net.ComponentGroup.4.8.DeveloperTools
--add Microsoft.Component.MSBuild
--add Microsoft.VisualStudio.Component.NuGet
--add Microsoft.NetCore.Component.SDK
--wait --passive --norestart
"""
update_args = " ".join(update_args.split())


def ensure_bootstrapper():
    """Check if bootstrapper exists in tmp folder, otherwise, download it to there."""

    # get temp directory
    tmp = os.getenv("TEMP")
    tmpname = os.path.join(tmp, os.path.basename(bootstrapper))
    if os.path.isfile(tmpname):
        return tmpname

    # download bootstrapper using requests library
    print(f"Downloading bootstrapper to {tmpname}")
    r = requests.get(bootstrapper)
    r.raise_for_status()
    with open(tmpname, "wb") as f:
        f.write(r.content)

    return tmpname


def install_vs():
    """Install visual studio"""

    # ensure bootstrapper exists
    bootstrapper = ensure_bootstrapper()

    # run bootstrapper
    subprocess.run(f"{bootstrapper} {install_args}", shell=True, check=True)
    echo("Visual studio installed.")


def update_vs():
    """Install visual studio"""

    # ensure bootstrapper exists
    bootstrapper = ensure_bootstrapper()

    # run bootstrapper
    r = subprocess.run(f"{bootstrapper} {update_args}", shell=True)
    # it will fail with exit status 1 if it is already up to date
    if r.returncode not in (0, 1):
        r.check_returncode()

    if r.returncode == 1:
        echo("Visual studio is already up to date.")
    else:
        echo("Visual studio updated.")


@click.group()
def vstudio():
    """Manage visual studio."""
    pass


@vstudio.command()
def install():
    """Install visual studio."""
    install_vs()


@vstudio.command()
def update():
    """Update visual studio."""
    update_vs()
