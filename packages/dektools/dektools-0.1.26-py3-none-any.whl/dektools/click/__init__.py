import typer
from . import hash as hash_command
from . import file as file_command
from . import net as net_command
from . import version as version_command

app = typer.Typer(add_completion=False)

app.add_typer(hash_command.app, name='hash')
app.add_typer(file_command.app, name='file')
app.add_typer(net_command.app, name='net')
app.add_typer(version_command.app, name='version')
