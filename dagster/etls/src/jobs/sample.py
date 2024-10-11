from datetime import datetime
from dagster import AutoMaterializePolicy, FreshnessPolicy, asset, get_dagster_logger

logger = get_dagster_logger()


@asset(
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=60 * 24 * 90),
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def pipeline_cluster():
    logger.info(f"Running pipeline_cluster at {datetime.now()} 😂")


if __name__ == "__main__":
    try:
        pipeline_cluster()
    except Exception as e:
        logger.error(e)
