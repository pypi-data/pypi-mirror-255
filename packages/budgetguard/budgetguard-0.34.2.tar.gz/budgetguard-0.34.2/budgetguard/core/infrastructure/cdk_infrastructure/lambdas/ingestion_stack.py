from aws_cdk import Stack
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_ecr as _ecr
from aws_cdk import aws_events as _events
from aws_cdk import aws_events_targets as _events_targets
from aws_cdk import aws_iam as _iam
from aws_cdk import Aws, Duration
from constructs import Construct


class IngestionLambdaStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, image_name: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.build_lambda_func(self.get_lambda_image(image_name))

    def get_lambda_image(self, image_name: str):
        ecr_repository = _ecr.Repository.from_repository_attributes(
            self,
            id="ECR",
            repository_arn="arn:aws:ecr:{0}:{1}:repository".format(
                Aws.REGION, Aws.ACCOUNT_ID
            ),
            repository_name=image_name,
        )
        ecr_image = _lambda.DockerImageCode.from_ecr(
            repository=ecr_repository,
            tag="latest",
            cmd=[
                "budgetguard.core.lambda_functions.ingestion.lambda_handler"
            ],  # noqa
            entrypoint=["python", "-m", "awslambdaric"],
        )
        return ecr_image

    def build_lambda_func(self, lambda_image: _lambda.Code):
        ingestion_lambda = _lambda.DockerImageFunction(
            scope=self,
            id="IngestionLambda",
            function_name="IngestionLambda",
            code=lambda_image,
            timeout=Duration.seconds(300),
            memory_size=1024,
        )
        ingestion_lambda.add_to_role_policy(
            _iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject"],
                resources=["arn:aws:s3:::budget-guard-ingest/*"],
                effect=_iam.Effect.ALLOW,
            )
        )
        ingestion_lambda.add_to_role_policy(
            _iam.PolicyStatement(
                actions=["secretsmanager:GetSecretValue"],
                resources=[
                    "arn:aws:secretsmanager:us-east-1:327077392103:secret:budget_guard_nordigen_key-OCfS6T"  # noqa
                ],
                effect=_iam.Effect.ALLOW,
            )
        )
        # Rule to trigger the lambda every day at 1 AM
        rule = _events.Rule(
            self,
            id="IngestionRule",
            rule_name="IngestionRule",
            schedule=_events.Schedule.cron(
                minute="0", hour="1", month="*", week_day="*", year="*"
            ),
        )
        rule.add_target(_events_targets.LambdaFunction(ingestion_lambda))
