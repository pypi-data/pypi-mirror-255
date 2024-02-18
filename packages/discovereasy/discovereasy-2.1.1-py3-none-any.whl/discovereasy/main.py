import typer
from .opportunity_tree import main as opportunity_tree_main
from .assumptions import main as assumptions_main

app = typer.Typer()
app.command(name='opportunity-tree')(opportunity_tree_main)
app.command(name='assumptions')(assumptions_main)

if __name__ == '__main__':
    app()
