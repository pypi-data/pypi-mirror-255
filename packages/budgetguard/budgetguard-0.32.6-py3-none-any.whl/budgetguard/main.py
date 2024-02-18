import argparse
import sys
import os
from core.pipelines.pipeline import Pipeline
from dotenv import load_dotenv

here = os.path.dirname(__file__)

sys.path.append(os.path.join(here, ".."))


parser = argparse.ArgumentParser()

parser.add_argument(
    "-pid",
    "--partition-id",
    help="The partition of the datalake to read from.",
    type=str,
    required=True,
)

parser.add_argument(
    "-t",
    "--task",
    help="The task to run.",
    type=str,
    required=True,
)


def run_task(pipeline: Pipeline):
    pipeline.run()


def run(task: str, partition_id: str):
    load_dotenv()
    if task == "ingest_account_data":
        from core.pipelines.ingest_account_data import (
            IngestAccountData,
        )

        pipeline = IngestAccountData(partition_id)
    elif task == "bronze_to_silver_balances":
        from core.pipelines.bronze_to_silver.balances_pipeline import (
            BronzeToSilverBalancesPipeline,
        )

        pipeline = BronzeToSilverBalancesPipeline(partition_id)
    elif task == "bronze_to_silver_details":
        from core.pipelines.bronze_to_silver.details_pipeline import (
            BronzeToSilverDetailsPipeline,
        )

        pipeline = BronzeToSilverDetailsPipeline(partition_id)
    elif task == "bronze_to_silver_transactions":
        from core.pipelines.bronze_to_silver.transactions_pipeline import (
            BronzeToSilverTransactionsPipeline,
        )

        pipeline = BronzeToSilverTransactionsPipeline(partition_id)
    elif task == "bronze_to_silver_metadata":
        from core.pipelines.bronze_to_silver.metadata_pipeline import (
            BronzeToSilverMetadataPipeline,
        )

        pipeline = BronzeToSilverMetadataPipeline(partition_id)
    else:
        raise ValueError(f"Unknown task: {task}")
    run_task(pipeline=pipeline)


if __name__ == "__main__":
    args = parser.parse_args()
    run(args.task, args.partition_id)
