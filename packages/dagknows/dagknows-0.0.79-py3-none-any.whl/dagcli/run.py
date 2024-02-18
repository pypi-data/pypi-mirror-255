
import typer, time
from enum import Enum
from dagcli.client import newapi
from dagcli.utils import present
from dagcli.transformers import *
from typing import List

app = typer.Typer()

@app.command()
def run(ctx: typer.Context,
        python_file = type.Argument(..., help = "Python file to submit for running")):
    """ Gets one or more jobs given IDs.  If no IDs are specified then a list of all jobs are returned."""
    # ctx.obj.tree_transformer = lambda obj: rich_job_info(obj["job"])
    present(ctx, newapi(ctx.obj, f"/jobs/{job_id}", { }, "GET"))

