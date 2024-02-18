import typer
from typer_htcondor import eventlog
from typer_htcondor import job
app = typer.Typer()
app.add_typer(eventlog.app, name="eventlog", help="Commands to work with event logs")
app.add_typer(job.app, name="job", help="Commands to work with jobs")

if __name__ == "__main__":
    app()
