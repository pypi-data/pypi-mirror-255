from budgetguard.main import run
from loguru import logger
from datetime import datetime
from datetime import timedelta


def lambda_handler(event, context):
    logger.info("Starting master exchange rates lambda..")
    task = "master_exchange_rates"
    yesterday = datetime.now() - timedelta(days=1)
    partition_id = yesterday.strftime("%Y%m%d")
    logger.info(f"Running task: {task} for partition: {partition_id}")
    run(task, partition_id)
