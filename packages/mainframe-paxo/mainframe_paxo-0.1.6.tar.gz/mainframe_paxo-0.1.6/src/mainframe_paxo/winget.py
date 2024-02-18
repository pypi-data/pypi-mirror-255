import subprocess

# stuff to install with winget


def install(id, force=False, upgrade=False):
    cmd = ["winget", "install", "-e", "--id", id]
    if force:
        cmd.append("--force")
    if upgrade:
        cmd[1] = "upgrade"
    subprocess.run(cmd)
