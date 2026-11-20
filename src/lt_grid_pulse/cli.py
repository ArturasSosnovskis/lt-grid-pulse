import typer

app = typer.Typer()

@app.command()
def hello(name:str, formal: bool = False):
    """Welcoming the given name, formal or not"""
    if formal:
        print(f"Good day, Mr. {name}")
    else:
        print(f"Hello {name}!")

@app.callback()
def callback():
    pass

