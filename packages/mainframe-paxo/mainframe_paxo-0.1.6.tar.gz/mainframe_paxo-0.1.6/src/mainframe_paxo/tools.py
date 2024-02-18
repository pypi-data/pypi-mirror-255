import os
import subprocess
import sys
import tkinter.messagebox
import winreg

import click

from . import config

# some common environment tools for us


def validate_drivename(drivename, check_exists=True):
    drivename = drivename.upper().strip()
    if not drivename.endswith(":"):
        drivename += ":"
    if check_exists:
        if not os.path.isdir(os.path.join(drivename, "\\")):
            raise ValueError(f"Drive {drivename} does not exist")
    return drivename


def workdrive_set(drivename):
    drivename = validate_drivename(drivename)
    env_var_set("PD_WORKDRIVE", drivename)


def workdrive_get(empty_ok=False):
    drivename = env_var_get("PD_WORKDRIVE")
    if not drivename and not empty_ok:
        raise ValueError("PD_WORKDRIVE not set.  Did you run initial-setup?")
    return drivename


# work location related stuff
def location_set(location):
    if location not in config.locations.keys():
        raise ValueError(f"Unknown location {location}")
    env_var_set("PD_LOCATION", location)


def location_get(empty_ok=False):
    location = env_var_get("PD_LOCATION")
    if not location:
        if empty_ok:
            return None
        raise ValueError("PD_LOCATION not set.  Did you run initial-setup?")
    if location not in config.locations.keys():
        raise ValueError(f"Unknown location {location}")
    return location


# setting and getting environment variables
def env_var_get(name):
    if name in os.environ:
        return os.environ[name]

    # the env var may have been set in a previous session
    # and not yet updated in _out_ environment. so we look
    # in the registry.
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        value, _ = winreg.QueryValueEx(key, name)
        return value
    except FileNotFoundError:
        pass

    # try the system environment
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
        )
        value, _ = winreg.QueryValueEx(key, name)
        return value
    except FileNotFoundError:
        pass
    return None


def env_var_set(name, value, permanent=True, system=False):
    if permanent:
        cmd = ["setx", name, value]
        if system:
            cmd.append("/m")
        subprocess.run(cmd, check=True, capture_output=True)
    os.environ[name] = value


def env_var_del(name, permanent=True, system=False):
    if not permanent:
        try:
            del os.environ[name]
        except KeyError:
            pass
    if not permanent:
        return

    if system:
        root = winreg.HKEY_LOCAL_MACHINE
        env = "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"
    else:
        root = winreg.HKEY_CURRENT_USER
        env = "Environment"
    try:
        key = winreg.OpenKey(root, env, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, name)
    except FileNotFoundError:
        pass


def addpath(path, permanent=False, system=False, infront=False):
    if infront:
        path = path + ";" + os.environ["PATH"]
    else:
        path = os.environ["PATH"] + ";" + path
    env_var_set("PATH", path, permanent, system)


# Subst!  This is a key feature of paxo.
# The user selects a a work drive, e.g. D:, with plenty of room.
# We then ensure that it has a folder called D:\paxdei_dev, and
# we subst that to P:\


def subst_drive(work_drive=None, force=False):
    """Subst the paxdei root folder to the subst-drive drive"""
    # Q will have the structure
    # Q:\.paxo   # this is a marker file to identify it.
    # Q:\paxdei
    # Q:\UE
    # Q:\otherstuff

    work_drive = work_drive or workdrive_get(empty_ok=False)
    validate_drivename(work_drive)

    # ensure the src folder exists
    src = os.path.join(work_drive, config.work_drive_dev_folder)
    os.makedirs(src, exist_ok=True)

    # ensure that it contains the .paxo file
    with open(os.path.join(src, ".paxo"), "w") as f:
        f.write("This is the paxo work drive")

    drive = subst_drive_get()
    out = subprocess.run(["subst", drive, src], capture_output=True)
    if out.returncode == 0:
        workdrive_set(work_drive)
        return True

    if "already" not in out.stdout.decode():
        out.check_returncode()

    if force:
        subprocess.run(["subst", drive, "/d"], check=True)
        subprocess.run(["subst", drive, src], check=True)
        workdrive_set(work_drive)
        return True
    return False


def subst_drive_check(drive):
    """Check if drive is a subst drive"""
    drive = drive or subst_drive_get()
    drive = validate_drivename(drive, check_exists=False)

    # if drive does not exist, we are ok
    if not os.path.isdir(drive):
        return True

    # if drive exists, we need to check if it is a subst drive
    target = is_subst(drive)
    if not target:
        raise click.ClickException(
            f"Intended subst drive {drive} exists, but is not a subst drive.  Please run 'paxo subst-drive' to select another."
        )

    # look for the .paxo file
    if not os.path.isfile(os.path.join(drive, ".paxo")):
        raise click.ClickException(
            f"Intended subst drive {drive} exists, but is not a paxo subst drive.  Please run paxo 'subst-drive' to select another."
        )

    return True


def subst_drive_get():
    drive = env_var_get("PD_SUBST_DRIVE")
    if not drive:
        drive = config.subst_drive_name
        subst_drive_set(drive)
    return drive


def subst_drive_set(drive):
    drive = validate_drivename(drive, check_exists=False)
    subst_drive_check(drive)
    env_var_set("PD_SUBST_DRIVE", drive)


def is_subst(drive):
    """Check if drive is a subst drive"""
    drive = validate_drivename(drive, check_exists=False)
    out = subprocess.run(["subst"], capture_output=True)
    for line in out.stdout.decode().splitlines():
        if line.startswith(drive):
            # return the part on the right side of the subst
            return line.split("=>")[1].strip()


def click_main(command, **extra_args):
    """run a click executable with an optional exception handler for no-console"""
    # do an initial check for --gui flags here because they have not been parsed yet
    if "--gui" in sys.argv[1:]:
        gui = True
    elif "--no-gui" not in sys.argv[1:]:
        gui = False
    else:
        gui = sys.executable.endswith("pythonw.exe")
    if gui:
        try:
            return command.main(standalone_mode=False, **extra_args)
        except click.Abort:
            tkinter.messagebox.showinfo("Aborted", "Operation aborted.")
            sys.exit(1)
        except click.ClickException as e:
            tkinter.messagebox.showerror("Error", e.format_message())
            sys.exit(e.exit_code)
        except Exception as e:
            tkinter.messagebox.showerror("Error", str(e))
            raise
    else:
        return command(**extra_args)
