from aws_cdk import core as cdk
from aws_cdk import aws_ec2 as ec2
import permissions
from compute import make_ec2_instance
from sg import make_security_group


class CloudwatchLabStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a role for our ec2 instance allowing them access to
        role = permissions.access_cloudwatch(self)

        # Create the security group
        vpc = ec2.Vpc.from_lookup(self, "default_vpc", is_default=True)
        security_group = make_security_group(self, vpc)

        # Create the ec2 instance
        instance = make_ec2_instance(self, role, vpc, security_group)

        # Output the ssh name to the instance
        cdk.CfnOutput(
            self, id="instance-ssh-name", value=instance.instance_public_dns_name
        )
