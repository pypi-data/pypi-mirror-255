from aws_cdk import Stack, Duration, RemovalPolicy
from constructs import Construct
from aws_cdk import aws_ecr as ecr


class BudgetGuardECRStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an ECR repository
        self.repository = ecr.Repository(
            self,
            "BudgetGuardRepository",
            repository_name="budget-guard",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
        )

        self.repository.add_lifecycle_rule(
            max_image_age=Duration.days(14),
            tag_status=ecr.TagStatus.ANY,
        )


class BudgetGuardEMRECRStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an ECR repository
        self.repository = ecr.Repository(
            self,
            "BudgetGuardEMRRepository",
            repository_name="budget-guard-emr",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_images=True,
        )

        self.repository.add_lifecycle_rule(
            max_image_age=Duration.days(14),
            tag_status=ecr.TagStatus.ANY,
        )
