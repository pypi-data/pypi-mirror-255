import typer
from typing import Annotated, List
import pkgutil
import pathlib
import subprocess

rooms_arg = typer.Argument(help="The lab rooms to generate IP ranges for. "
                                "The lab room is the hostname prefix, eg red "
                                "(for Röd) or toke (for Toker).")

def add_command(cli):
  """
  Adds the [[iprange]] command to the given [[cli]].
  """
  @cli.command()
  def iprange(rooms: Annotated[List[str], rooms_arg]):
    """
    Generate the IP ranges for the given lab rooms.
    """
    package_path = pathlib.Path(pkgutil.get_loader(__name__).path).parent
    iprange_sh = package_path / "iprange.sh"
    subprocess.run([iprange_sh, *rooms], check=True)

if __name__ == "__main__":
  cli = typer.Typer()
  add_command(cli)
  cli()
