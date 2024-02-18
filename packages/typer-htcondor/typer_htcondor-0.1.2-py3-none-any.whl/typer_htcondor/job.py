import typer

app = typer.Typer()

@app.command()
def submit():
    typer.echo("Submitting a job")