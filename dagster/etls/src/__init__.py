from dagster import load_assets_from_package_module
from . import jobs

JOBS = "jobs"
src_jobs = load_assets_from_package_module(package_module=jobs, group_name=JOBS)
