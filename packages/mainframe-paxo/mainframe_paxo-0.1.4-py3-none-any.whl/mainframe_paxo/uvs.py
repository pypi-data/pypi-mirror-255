import subprocess
import sys
import tkinter.messagebox
from typing import Optional

import click

from . import tools, ue

# our custom version of UnrealVersionSelector.exe

use_gui = sys.executable.endswith("pythonw.exe")


@click.group(invoke_without_command=False)
@click.option("--gui/--no-gui", default=use_gui, help="run with or without gui")
@click.pass_context
def uvs(ctx, gui):
    """A python version of the UnrealVersionSelector.exe.
    
    Initial command can be prefixed with a single dash or slash."""
    global use_gui
    use_gui = gui

    if ctx.invoked_subcommand is None:
        # if this were part of engine, we could register _this_ engine with prompt
        # but since it's not, we don't support this functionality
        # of invoking UnrealVersionSelector.exe with no arguments.
        pass
cli = uvs

@cli.command()
@click.option("--unattended", is_flag=True, help="Don't prompt for input")
@click.argument("engine_id", default=None)
def register(engine_id, unattended):
    """Register a _this_ engine.  Not supported."""
    click.echo("can't register _this_engine, because _this_ is not an engine")
    sys.exit(1)


# flags are non-standard extensions to the original UnrealVersionSelector.exe
@cli.command()
@click.option("--check", is_flag=True, help="Check current registrations.")
@click.option("--clear", is_flag=True, help="Remove associations.")
@click.option("--user", is_flag=True, help="use 'user' scope instead of 'machine'")
def fileassociations(check, clear, user):
    """Register file associations"""
    # TODO: call registry functions i ue module


# non-standard extension to the original UnrealVersionSelector.exe
@cli.command()
@click.argument("uproject", type=click.Path(exists=True), metavar="<.uproject>")
def identifier(uproject):
    """Print the identifier for the project"""
    identifier = ue.get_identifier(uproject)
    click.echo(identifier)


# non-standard extension to the original UnrealVersionSelector.exe
@cli.command()
@click.argument("uproject", type=click.Path(exists=True), metavar="<.uproject>")
def engineroot(uproject):
    """Print the engine root for the project"""
    root = ue.find_engine_for_project(uproject)
    click.echo(root)


@cli.command()
@click.argument("uproject", type=click.Path(exists=True), metavar="<.uproject>")
@click.option(
    "--engine_id", metavar="<engine_id>", default=None, help="The engine id to use"
)
def switchversion(uproject, engine_id):
    """Switch the engine version for the project"""
    # TODO, perform this interactive operation
    if engine_id:
        # switch_engine_id_silent(uproject, engine_id)
        pass
    else:
        # switch_engine_id_prompt(uproject)
        pass


@cli.command()
@click.argument("uproject", type=click.Path(exists=True), metavar="<.uproject>")
@click.argument("engine_id", nargs=1, metavar="<engine_id>")
def switchversionsilent(uproject, engine_id):
    """Switch set the engine-id for this project to a given engine-id without prompting"""
    # TODO, perform this interactive operation
    # switch_engine_id_silent(uproject, engine_id)
    pass


@cli.command()
@click.argument("uproject", type=click.Path(exists=True), metavar="<.uproject>")
def editor(uproject):
    """Start the editor for project"""
    editor = ue.get_editor_from_uproject()
    if editor:
        result = subprocess.run([editor, uproject])
        sys.exit(result.returncode)
    else:
        click.echo("No editor found")
        sys.exit(1)


@cli.command()
@click.argument("uproject", type=click.Path(exists=True), metavar="<.uproject>")
def projectlist(uproject):
    """Start the editor with a list of projects"""
    editor = ue.get_editor_from_uproject()
    if editor:
        result = subprocess.run([editor])
        sys.exit(result.returncode)
    else:
        click.echo("No editor found")
        sys.exit(1)


@cli.command()
@click.argument("uproject", type=click.Path(exists=True), metavar="<.uproject>")
def game(uproject):
    """Start the editor for the project and run the game"""
    editor = ue.get_editor_from_uproject()
    if editor:
        result = subprocess.run([editor, uproject, "-game"])
        sys.exit(result.returncode)
    else:
        click.echo("No editor found")
        sys.exit(1)


@cli.command()
@click.argument("uproject", type=click.Path(exists=True), metavar="<.uproject>")
def projectfiles(uproject):
    """Rebuild project files for the project"""
    # editor = ue.get_editor_from_uproject()
    pass


@cli.command()
@click.argument("uproject", type=click.Path(exists=False), metavar="<.uproject>")
def test(uproject):
    messagebox_ok("This is a test message", True)
    messagebox_ok("This is a test message", False)


@cli.command()
def register_test():
    """Register uvs as the default UnrealVersionSelector"""
    #print(sys.argv)
    return
    # find the command used to run us
    cmd = sys.argv[:]
    i = cmd.index("register-test")
    cmd = cmd[:i]
    # remove any trailing args
    while cmd[-1].startswith("-"):
        cmd.pop()

    # if we are running a .py file, we need to use the -m flag with the actual
    # module name (not __main__)
    if cmd[0].endswith(".py"):
        exe = sys.executable
        if exe.endswith("python.exe"):
            exe = exe[:-10] + "pythonw.exe"
        cmd = [exe, "-m", __spec__.name] + cmd[1:]

    ue.register_uproject_handler(engine_path=None, handler=cmd, test=True)


def main():
    # ignore initial double dash arguments though, which are
    # global
    i = 1
    while i < len(sys.argv) and sys.argv[i].startswith("--"):
        i += 1

    # now we get to the command.  strip a single / or - from it.
    if len(sys.argv) > i:
        # turn slash option into a command, stripping the slash
        if sys.argv[i].startswith("/"):
            sys.argv[i] = sys.argv[i][1:]
        elif sys.argv[i].startswith("-") and not sys.argv[i].startswith("--"):
            sys.argv[i] = sys.argv[i][1:]

    # also allow single dash options, by turning them into two dash options
    for i, arg in enumerate(sys.argv[1:]):
        if arg.startswith("-") and not arg.startswith("--"):
            sys.argv[i + 1] = f"--{arg[1:]}"

    tools.click_main(cli, obj={})


def messagebox_ok(
    message: str, success: bool = True, heading: Optional[str] = None
) -> bool:
    if not heading:
        heading = "Success" if success else "Error"

    if use_gui:
        if success:
            tkinter.messagebox.showinfo(heading, message)
        else:
            tkinter.messagebox.showerror(heading, message)
    else:
        # just use echo
        if success:
            click.echo(message)
        else:
            click.echo(
                click.style(f"{heading}:", fg="red") + f" {message}", file=sys.stderr
            )

    return success


if __name__ == "__main__":
    main()
