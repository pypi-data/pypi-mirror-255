import glob
import json
import os.path
import subprocess
import sys
import winreg
from contextlib import contextmanager

import click
from click import echo, secho

from . import p4, tools
from .registry import Key
from .uebase.desktop import enumerate_engine_installations, is_valid_root_directory


# helper to close winreg keys
@contextmanager
def close_key(key):
    try:
        yield key
    finally:
        key.Close()


# various tools for setting up UE environment and running it.abs


@click.group()
@click.pass_context
def ue(ctx):
    """work with Unreal Engine"""


@ue.group()
@click.option(
    "--engine-path",
    type=click.Path(exists=False),
    default=lambda: p4.get_engine_path(),
    help="The path to register if not default engine path.",
)
@click.option(
    "--scope",
    type=click.Choice(["user", "machine"]),
    default="user",
    help="Work with user or machine registry",
)
@click.option(
    "--check/--no-check", is_flag=True, help="Only accept valid engine paths."
)
@click.pass_context
def engine(ctx, engine_path, scope, check):
    """work with engine registration"""
    ctx.ensure_object(dict)
    ctx.obj["engine_path"] = engine_path
    ctx.obj["scope"] = scope
    ctx.obj["reg_root"] = (
        winreg.HKEY_CURRENT_USER if scope == "user" else winreg.HKEY_LOCAL_MACHINE
    )
    ctx.obj["check"] = check


@ue.command()
def setup():
    setup_ue(tools.workdrive_get(), p4.get_engine_path(), tools.location_get())


@engine.command("register")
@click.pass_context
@click.option("--engine-id", type=str, metavar="<id-string>", default=None)
def engine_register(ctx, engine_id):
    check = ctx.obj["check"]
    register_engine(ctx.obj["engine_path"], engine_id, check=check)


@engine.command("deregister")
@click.argument("engine-id", type=str, metavar="<id-string>")
@click.pass_context
def engine_deregister(ctx, engine_id):
    deregister_engine(ctx.obj["engine_path"], engine_id)


@engine.command("list")
@click.pass_context
@click.option("--all", is_flag=True, help="List both user and machine registrations.")
def engine_list(ctx, all):
    user = ctx.obj["scope"] == "user"
    if user or all:
        print("User registered engines:")
        reg_root = winreg.HKEY_CURRENT_USER
        with Key(reg_root, "SOFTWARE\\Epic Games\\Unreal Engine\\Builds") as key:
            for name, value in key.items():
                print(f"{name} = {value[0]}")
    if not user or all:
        print("System registered engines:")
        reg_root = winreg.HKEY_LOCAL_MACHINE
        key = Key(reg_root, "SOFTWARE\\EpicGames\\Unreal Engine")
        if key:
            with key:
                for subkey in key.subkeys():
                    with subkey:
                        print(f"{subkey.name} = {subkey['InstalledDirectory']}")


@engine.command("lookup")
@click.pass_context
@click.argument("engine-id", type=str, metavar="<id-string>")
@click.option(
    "--all/--no-all",
    is_flag=True,
    default=True,
    help="Look up in both user and machine registrations.",
)
def engine_lookup(ctx, engine_id, all, check):
    user = ctx.obj["scope"] == "user"
    path = None
    if user or all:
        reg_root = winreg.HKEY_CURRENT_USER
        with Key(reg_root, "SOFTWARE\\Epic Games\\Unreal Engine\\Builds") as key:
            if key:
                path = key.get(engine_id, None)
    if path is not None and check and not is_valid_root_directory(path):
        path = None
    if path is None and (not user or all):
        reg_root = winreg.HKEY_LOCAL_MACHINE
        with Key(reg_root, "SOFTWARE\\EpicGames\\Unreal Engine") as key:
            if key:
                for subkey in key.subkeys():
                    with subkey:
                        if subkey.name == engine_id:
                            path = subkey["InstalledDirectory"]
                            break
    if path is not None and check and not is_valid_root_directory(path):
        path = None

    if path is not None:
        echo(path)
    sys.exit(1)


@ue.group()
@click.option("--scope", type=click.Choice(["user", "machine"]), default="user")
@click.pass_context
def uproject(ctx, scope):
    """work with .uproject files registration"""
    ctx.ensure_object(dict)
    ctx.obj["scope"] = scope


@uproject.command("set")
@click.pass_context
@click.option(
    "--verify/--no-verify", default=True, help="Verify that target files exist."
)
@click.option(
    "--engine-path",
    type=click.Path(exists=False),
    default=lambda: p4.get_engine_path(),
    help="The path to the handling Engine if not the default path.",
)
@click.option(
    "--handler",
    type=click.Path(exists=False),
    default=None,
    help="The path of a custom handler executable to use.",
)
def uproject_register(ctx, verify, engine_path, handler):
    user = ctx.obj["scope"] == "user"
    handler = register_uproject_handler(
        engine_path=engine_path, handler=handler, user=user, verify=verify
    )
    echo(f"set .uproject handler for {ctx.obj['scope']} to {handler!r}")


@uproject.command("get")
@click.pass_context
@click.option("-any/--no-any", default=True, help="Get the handler for any scope.")
@click.option(
    "--verify/--no-verify", default=True, help="Verify that target files exist."
)
def uproject_get(ctx, verify, any):
    scope = ctx.obj["scope"] if not any else "user"
    handler = get_uproject_handler(user=scope == "user", verify=verify)
    if not handler and any:
        scope = "machine"
        handler = get_uproject_handler(user=False, verify=verify)
    if handler:
        echo(f".uproject handler is set to {handler!r} for scope {scope!r} ")
        if not os.path.isfile(handler):
            secho(f"Warning: handler {handler!r} does not exist", fg="red")
    else:
        if not any:
            echo(f".uproject handler is not set for scope {scope!r} ")
        else:
            echo(".uproject handler is not set for any scope")


@uproject.command("show")
@click.pass_context
@click.option(
    "--verify/--no-verify", default=True, help="Verify that target files exist."
)
def uproject_show(ctx, verify):
    user = ctx.obj["scope"] == "user"
    check_uproject_handler(user=user, verify=verify)


@uproject.command("deregister")
@click.pass_context
def uproject_deregister(ctx):
    user = ctx.obj["scope"] == "user"
    deregister_uproject_handler(user=user)


def setup_ue(work_drive, engine_path, location=None):
    # set up the environment variables
    set_ddc_vars(work_drive, location)

    # register the engine
    if not os.path.isfile(os.path.join(engine_path, "build_info.json")):
        raise click.ClickException(
            f"Engine path {engine_path} does not contain an engine.  Have you performed a sync?"
        )

    register_uproject_handler(engine_path)
    register_engine(engine_path)

    # install prerequisites
    install_prerequisites(engine_path)


def set_location(location):
    # set the env vars related to location
    loc = tools.locations[location]
    ddc = loc["ddc"]
    if ddc:
        print(f"setting shared data cache path to {ddc} for location {location}")
        tools.env_var_set("UE-SharedDataCachePath", ddc)
    else:
        print(f"clearing shared data cache path for location {location}")
        tools.env_var_del("UE-SharedDataCachePath")


def set_ddc_vars(work_drive, location):
    # set local DDC location
    path = os.path.normcase(os.path.join(work_drive, "/DDC"))
    print(f"setting local data cache path to {path}")
    tools.env_var_set("UE-LocalDataCachePath", path)
    set_location(location)


def register_uproject_handler(
    engine_path=None, handler=None, user=True, verify=True, test=False
):
    # the engine contains a special execution to act as a shell handler
    # for files with the .uproject extension
    reg_root = winreg.HKEY_CURRENT_USER if user else winreg.HKEY_LOCAL_MACHINE

    cmdhandler = None
    if not handler:
        handler = os.path.join(
            engine_path, "Engine", "Binaries", "Win64", "UnrealVersionSelector.exe"
        )
        handler = os.path.abspath(handler)
        cmdhandler = os.path.join(
            engine_path, "Engine", "Binaries", "Win64", "UnrealVersionSelector-Cmd.exe"
        )
        handler = [handler]
        if not os.path.exists(cmdhandler):
            cmdhandler = None
        else:
            cmdhandler = [cmdhandler]
    else:
        # we have been given a custom handler,
        if not isinstance(handler, list):
            handler = [handler]
    handler[0] = os.path.abspath(handler[0])

    # we need to find an icon for the handler
    paxoicon = os.path.abspath(os.path.join(os.path.dirname(__file__), "paxo.ico"))
    iconhandler = handler[0]
    if not os.path.exists(handler[0]):
        if verify:
            raise click.ClickException(f"Could not find a handler at {handler[0]}")
        # use something else for the icon
        iconhandler = paxoicon
    # or, if it is not UnrealVersionSelector, use the icon from paxo
    if "UnrealVersion" not in os.path.basename(handler[0]):
        iconhandler = paxoicon

    cmdhandler = cmdhandler or handler

    # quoted handler for the registry
    quoted_handler = " ".join(f'"{f}"' for f in handler)
    quoted_cmdhandler = " ".join(f'"{f}"' for f in cmdhandler)

    quoted_iconhandler = f'"{iconhandler}"'
    quoted_paxoicon = f'"{paxoicon}"'

    # we must now find the appropriate place in the registry and add it.abs
    # this is a bit tricky, but we can use the python winreg module
    key = Key(reg_root, "SOFTWARE\\Classes\\.uproject")
    with key.create():
        key[""] = "Unreal.ProjectFile"

    with Key(reg_root, "SOFTWARE\\Classes\\Unreal.ProjectFile", create=True) as key:
        # we could well clear this subtree first and write it all fresh
        key[""] = "Unreal Engine Project File"
        key["VersionSelectorExecutable"] = quoted_handler
        key["VersionSelectorExecutableCmd"] = quoted_cmdhandler

        # the DefaultIcon subkey
        with key.create("DefaultIcon") as subkey:
            subkey[""] = quoted_iconhandler

        with key.create("shell") as subkey:
            with subkey.create("open") as subsubkey:
                subsubkey[""] = "Open"
                with subsubkey.create("command") as subsubsubkey:
                    subsubsubkey[""] = quoted_handler + ' /editor "%1"'

            with subkey.create("run") as subsubkey:
                subsubkey[""] = "Launch game"
                with subsubkey.create("command") as subsubsubkey:
                    subsubsubkey[""] = quoted_handler + ' /game "%1"'

            with subkey.create("rungenproj") as subsubkey:
                subsubkey[""] = "Generate Visual Studio project files"
                with subsubkey.create("command") as subsubsubkey:
                    subsubsubkey[""] = quoted_handler + ' /projectfiles "%1"'

            with subkey.create("switchversion") as subsubkey:
                subsubkey[""] = "Switch Unreal Engine version..."
                with subsubkey.create("command") as subsubsubkey:
                    subsubsubkey[""] = quoted_handler + ' /switchversion "%1"'

            with subkey.create("test") as subsubkey:
                subsubkey[""] = "run the user test thingie..."
                with subsubkey.create("command") as subsubsubkey:
                    subsubsubkey[""] = quoted_handler + ' /test "%1"'
                with subsubkey.create("icon") as subsubsubkey:
                    subsubsubkey[""] = quoted_paxoicon

            with subkey.create("hotdog") as subsubkey:
                subsubkey[""] = "Get some sausages..."
                with subsubkey.create("command") as subsubsubkey:
                    subsubsubkey[""] = "explorer.exe https://hot-dog.org"
                with subsubkey.create("Icon") as subsubsubkey:
                    subsubsubkey[""] = quoted_paxoicon

    # If the user has manually selected something other than our extension, we need to delete it. Explorer explicitly disables set access on that keys in that folder, but we can delete the whole thing.

    user_choice = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.uproject\\UserChoice"
    key = Key(winreg.HKEY_CURRENT_USER, user_choice)
    if key:
        key.delete(tree=True)
    return handler


def get_uproject_handler(user=True, verify=True):
    reg_root = winreg.HKEY_CURRENT_USER if user else winreg.HKEY_LOCAL_MACHINE

    def unquote(s):
        if s[0] == '"' and s[-1] == '"':
            s = s[1:-1]
        return s

    def check_handler(s, verify=False):
        if s[0] == '"' and s[-1] == '"':
            s = s[1:-1]
        else:
            print(f"Warning: string '{s}' is not quoted")
        if not os.path.isfile(s):
            print(f"Warning: {s} does not exist")
            if verify:
                raise click.ClickException(f"Could not find {s}")

    # we must now find the appropriate place in the registry and add it.abs
    # this is a bit tricky, but we can use the python winreg module
    with Key(reg_root, "SOFTWARE\\Classes\\.uproject") as key:
        if not key:
            return None
        cls = key[""]
        if not cls:
            return None

    with Key(reg_root, f"SOFTWARE\\Classes\\{cls}") as key:
        if not key:
            return None

        exe = key.get("VersionSelectorExecutable")
        if exe:
            return unquote(exe)

        # look for the "open" subkey
        with key.subkey(r"shell\open\command") as subkey:
            if not subkey:
                return None
            cmd = subkey[""]
            # we expect something like '"C:\Program Files\Epic Games\UE_4.26\Engine\Binaries\Win64\UnrealVersionSelector.exe" /editor "%1"'
            # split it into the exe and the args, taking care of quotes, ignoring spaces inside the quotes
            parts = cmd.split('"')
            return parts[1]


def check_uproject_handler(user=True, verify=True):
    # the engine contains a special execution to act as a shell handler
    # for files with the .uproject extension
    reg_root = winreg.HKEY_CURRENT_USER if user else winreg.HKEY_LOCAL_MACHINE

    def check_handler(s, verify=False):
        if s[0] == '"' and s[-1] == '"':
            s = s[1:-1]
        else:
            print(f"Warning: string '{s}' is not quoted")
        if not os.path.isfile(s):
            print(f"Warning: {s} does not exist")
            if verify:
                raise click.ClickException(f"Could not find {s}")

    # we must now find the appropriate place in the registry and add it.abs
    # this is a bit tricky, but we can use the python winreg module
    with Key(reg_root, "SOFTWARE\\Classes\\.uproject") as key:
        if not key:
            print(".uproject handler not registered")
        else:
            value = key[""]
            if value != "Unreal.ProjectFile":
                print(".uproject handler registered to something else")
            else:
                print(".uproject handler registered")

    with Key(reg_root, "SOFTWARE\\Classes\\Unreal.ProjectFile") as key:
        if not key:
            print("Unreal.ProjectFile handler not registered")
        else:
            print(f"Unreal.ProjectFile handler registered to {key['']!r}")
            try:
                exe = key["VersionSelectorExecutable"]
                print(f"VersionSelectorExecutable registered to {exe!r}")
                check_handler(exe, verify)
            except KeyError:
                exe = None

            with key.subkey("DefaultIcon") as subkey:
                if not subkey:
                    print("DefaultIcon not registered")
                else:
                    icon = subkey[""]
                    print(f"DefaultIcon registered to {icon!r}")
                    check_handler(icon, verify)

            with key.subkey("shell") as subkey:
                if not subkey:
                    print("shell not registered")
                else:
                    for subsubkey in subkey.subkeys():
                        with subsubkey:
                            print(
                                f"shell subkey {subsubkey.name} registered to '{subsubkey['']!r}'"
                            )
                            subsubsubkey = subsubkey.subkey("command")
                            if not subsubsubkey:
                                print(f"shell subkey {subsubkey.name} has no command")
                            else:
                                with subsubsubkey:
                                    print(
                                        f"shell subkey {subsubkey.name} command is  {subsubsubkey['']!r}"
                                    )
                            subsubsubkey = subsubkey.subkey("Icon")
                            if not subsubsubkey:
                                print(f"shell subkey {subsubkey.name} has no Icon")
                            else:
                                with subsubsubkey:
                                    print(
                                        f"shell subkey {subsubkey.name} Icon set to {subsubsubkey['']!r}"
                                    )
                                    check_handler(subsubsubkey[""], verify)

    if user:
        # If the user has manually selected something other than our extension, we need to delete it. Explorer explicitly disables set access on that keys in that folder, but we can delete the whole thing.
        user_choice = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.uproject\\UserChoice"
        key = Key(winreg.HKEY_CURRENT_USER, user_choice)
        if key:
            print(
                "User has default shell action for .uproject files.  Re-register to remove it"
            )
            key.print(tree=True)


def deregister_uproject_handler(user=True):
    # the engine contains a special execution to act as a shell handler
    # for files with the .uproject extension
    reg_root = winreg.HKEY_CURRENT_USER if user else winreg.HKEY_LOCAL_MACHINE

    Key(reg_root, "SOFTWARE\\Classes\\Unreal.ProjectFile").delete(tree=True)
    Key(reg_root, "SOFTWARE\\Classes\\.uproject").delete(tree=True)
    if user:
        Key(
            reg_root,
            "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.uproject\\UserChoice",
        ).delete(tree=True)


def register_engine(engine_path, engine_id=None, check=True):
    # read the engine registry name from the build_info.json file

    if check and not is_valid_root_directory(engine_path):
        raise click.ClickException(f"Engine path {engine_path} is not valid")

    if not engine_id:
        with open(os.path.join(engine_path, "build_info.json")) as f:
            info = json.load(f)
        engine_name = info["engine_id"]
    else:
        engine_name = engine_id

    # now open the registry key for the user
    key = Key(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Epic Games\\Unreal Engine\\Builds")
    with key.create():
        key[engine_name] = engine_path


def deregister_engine(engine_path=None, engine_id=None):
    if not engine_path and not engine_id:
        raise ValueError("Must specify either engine_path or engine_id")
    if not engine_id:
        assert not engine_id
        with open(os.path.join(engine_path, "build_info.json")) as f:
            info = json.load(f)
        engine_id = info["engine_id"]
    with Key(
        winreg.HKEY_CURRENT_USER,
        "SOFTWARE\\Epic Games\\Unreal Engine\\Builds",
        write=True,
    ) as key:
        if key:
            del key[engine_id]


def register_engine_old(engine_path):
    # we have a special engine registration tool in the engine folder
    tool = os.path.join(engine_path, "build-tools", "register_engine.cmd")
    subprocess.check_call([tool])


def install_prerequisites(engine_path):
    # we have a special engine registration tool in the engine folder
    tool = os.path.join(
        engine_path, "Engine", "Extras", "Redist", "en-us", "UE4PrereqSetup_x64.exe"
    )
    subprocess.check_call([tool, "/quiet"])


def start_editor(engine_path, project_path):
    # find the .uproject file in project_path
    uproject = glob.glob(os.path.join(project_path, "*.uproject"))[0]
    uproject = os.path.abspath(uproject)

    # find the ue executable
    ue = os.path.join(engine_path, "Engine", "Binaries", "Win64", "UnrealEditor.exe")

    # start the editor
    subprocess.check_call([ue, uproject])


# uproject engine registration stuff


def read_uproject(uproject):
    # read the .uproject file
    with open(uproject) as f:
        info = json.load(f)
    return info


def write_uproject(uproject, info):
    # write the .uproject file
    with open(uproject, "w") as f:
        json.dump(info, f, indent="\t")


def get_engine_association(uproject):
    # read the .uproject file
    info = read_uproject(uproject)
    engine = info.get("EngineAssociation", None)
    return engine


def set_engine_association(uproject, engine_identifier):
    # read the .uproject file
    info = read_uproject(uproject)
    if "EngineAssociation" in info:
        info["EngineAssociation"] = engine_identifier
    else:
        # recreate the dict, putting EngineAssociation at position 1 (after FileVersion)
        newinfo = {}
        for i, (key, value) in enumerate(info.items()):
            newinfo[key] = value
            if i == 0:
                newinfo["EngineAssociation"] = engine_identifier
        info = newinfo
    write_uproject(uproject, info)


def find_engine_for_project(uproject):
    """Finds the root of the engine to use for this uproject file"""
    engine_id = get_engine_association(uproject)
    if not engine_id:
        # this is a unified build, so we need to find the engine in
        # the parents
        return find_engine_in_parents(uproject)
    else:
        # guids are not engine paths, bypass the engine path test
        if not is_ue_engine_guid(engine_id):
            # first, check if the id is in fact a file path.
            # does it look like a path?  If it is not an absolute path, try to
            # use it relative to the project root
            engine_path = engine_id
            if not os.path.isabs(engine_path):
                engine_path = os.path.join(os.path.dirname(uproject), engine_id)
            if is_valid_root_directory(engine_path):
                return engine_path

        # no, not an engine path.  It must be an id, then.
        return look_up_engine(engine_id)


def is_ue_engine_guid(guid):
    """Check if this is a valid engine guid"""
    # unreal guids are 38 chars, hex digits, with dashes
    if len(guid) != 38:
        return False
    if not guid.startswith("{") and not guid.endswith("}"):
        return False
    return True


def find_engine_in_parents(uproject):
    """Given an uproject, search up the hierarhcy until an engine is found"""
    uproject = os.path.abspath(uproject)
    project_folder = os.path.dirname(uproject)
    current = os.path.dirname(project_folder)
    last = ""
    # loop until we can reach no higher
    while current != last:
        last = current
        # check if this folder contains an engine
        if is_valid_root_directory(current):
            # found the engine
            return current
        # go up a level
        current = os.path.dirname(current)


def look_up_engine(engine_id):
    """Look up the engine path from the registry"""
    engines = enumerate_engine_installations()
    return engines.get(engine_id, None)


def get_editor_path(engine_path):
    """Get the path to the editor executable"""
    editor = os.path.join(
        engine_path, "Engine", "Binaries", "Win64", "UnrealEditor.exe"
    )
    if os.path.isfile(editor):
        return editor


def get_editor_from_uproject(uproject):
    """Get the path to the editor executable from the uproject file"""
    engine_path = find_engine_for_project(uproject)
    if not engine_path:
        return None
    return get_editor_path(engine_path)


"""
# project file generation
def generate_project_file(engine_dir, uproject, warn, log_file_path):
{
	arguments = " -projectfiles"

    project_directory = ProjectDirectory.get(engine_dir)

	# Build the arguments to pass to UBT. If it's a non-foreign project, just build full project files.
	if ( uproject and  project_directory.is_foreign_project(uproject) ):
		# Figure out whether it's a foreign project
		const FUProjectDictionary &ProjectDictionary = GetCachedProjectDictionary(RootDir);
		if(ProjectDictionary.IsForeignProject(ProjectFileName))
		{
			Arguments += FString::Printf(TEXT(" -project=\"%s\""), *IFileManager::Get().ConvertToAbsolutePathForExternalAppForRead(*ProjectFileName));

			// Always include game source
			Arguments += TEXT(" -game");

			// Determine whether or not to include engine source
			if(IsSourceDistribution(RootDir))
			{
				Arguments += TEXT(" -engine");
			}
			else
			{
				// If this is used within UnrealVersionSelector then we still need to pass
				// -rocket to deal with old versions that don't use Rocket.txt file
				Arguments += TEXT(" -rocket");
			}
		}
	}
	Arguments += TEXT(" -progress");

	if (!LogFilePath.IsEmpty())
	{
		Arguments += FString::Printf(TEXT(" -log=\"%s\""), *LogFilePath);
	}

	// Compile UnrealBuildTool if it doesn't exist. This can happen if we're just copying source from somewhere.
	bool bRes = true;
	Warn->BeginSlowTask(LOCTEXT("GeneratingProjectFiles", "Generating project files..."), true, true);
	if(!FPaths::FileExists(GetUnrealBuildToolExecutableFilename(RootDir)))
	{
		Warn->StatusUpdate(0, 1, LOCTEXT("BuildingUBT", "Building UnrealBuildTool..."));
		bRes = BuildUnrealBuildTool(RootDir, *Warn);
	}
	if(bRes)
	{
		Warn->StatusUpdate(0, 1, LOCTEXT("GeneratingProjectFiles", "Generating project files..."));
		bRes = RunUnrealBuildTool(LOCTEXT("GeneratingProjectFiles", "Generating project files..."), RootDir, Arguments, Warn);
	}
	Warn->EndSlowTask();
	return bRes;
}
"""
