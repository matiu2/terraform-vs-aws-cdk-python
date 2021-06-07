"""
Creates a role for our EC2 instance that enables it to talk to cloudwatch
"""
from aws_cdk import aws_iam as iam


def access_cloudwatch(scope):
    """
    Returns an instance profile that allows an ec2 instance to access cloudwatch
    """
    policy = iam.ManagedPolicy.from_managed_policy_arn(
        scope, "allow-cloudwatch", "arn:aws:iam::aws:policy/CloudWatchFullAccess"
    )

    role = iam.Role(
        scope,
        "allow-cloudwatch-access",
        description="Allows ec2 instances to access cloudwatch",
        assumed_by=iam.ServicePrincipal(
            service="ec2.amazonaws.com", region=scope.region
        ),
    )
    return role
