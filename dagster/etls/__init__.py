import os
from dagster import Definitions
from .src import src_jobs

all_jobs = [*src_jobs]
defs = Definitions(
    assets=all_jobs,
    executor=None,
    resources={},
)
