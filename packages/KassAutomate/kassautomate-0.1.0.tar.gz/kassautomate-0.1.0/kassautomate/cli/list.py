from rich.console import Console
from rich.table import Table
from typer import Typer
from rich import inspect

console = Console()
app = Typer()


@app.command()
def hello(name: str):
    """fsfsdfsdfghsdfjsdfhjk"""

    inspect(name, methods=True)
    console.print(f"Hello {name}", style="bold red")


@app.command()
def goodbye(name: str, formal: bool = False):
    """Exibe uma frase de despedida"""
    if formal:
        console.print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        console.print(f"Bye {name}!")
