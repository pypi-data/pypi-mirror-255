import typer
from ..version import version_digits

app = typer.Typer(add_completion=False)


@app.command(name='port')
def digits(version):
    print(version_digits(version), flush=True)
