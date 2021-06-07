This compares terraform and aws-cdk for a small deployment.

We're building a lab for the [udemy course for AWS SysOps Associate](https://www.udemy.com/course/aws-certified-sysops-administrator-associate/learn/lecture/2691470?start=195#overview)

All we need is:

 * An EC2 instance
   + An ssh key to sign into it
   + A role that allows it to run cloudwatch operations
   + A bootstrap userdata file (you have to sign up for the couse to get it)
   + A security group allowing SSH from my house and outgoing http and https to anywhere

# Summary

## Times

 * CDK:
   + Deploy: 3m 16s
   + Destroy: 59s
 * Terraform:
   + Deploy: 1m 6s
   + Destroy: 1m 3s

## Reasons I prefer Terraform

 * It easily allows me to read my ssh public key and create a new ec2 keypair from it as part of the deployment
   + AWS CDK requires you either use a [3rd party python
     library](https://pypi.org/project/cdk-ec2-key-pair/) to generate a
     key-pair inside of AWS, then download the private key to use it, or have a
     pre-existing key. I went with the pre-existing key route.
 * The terraform language is more purpose created, explicit and easier to follow. This is important when approving PRs for important infrastructure changes

# Code comparison

## Security group

### Terraform

Terraform is more code, but I like it better because it's more readable and standardized

```hcl
resource "aws_security_group" "cloud_watch" {
  name = "cloud_watch"
}

resource "aws_security_group_rule" "ingress" {
  for_each = {
    ssh   = 22
    http  = 80
    https = 443
  }
  security_group_id = aws_security_group.cloud_watch.id
  type              = "ingress"
  protocol          = "tcp"
  from_port         = each.value
  to_port           = each.value
  cidr_blocks       = [local.my_cidr]
}

resource "aws_security_group_rule" "egress" {
  for_each = {
    http  = 80
    https = 443
  }
  security_group_id = aws_security_group.cloud_watch.id
  type              = "egress"
  protocol          = "tcp"
  from_port         = each.value
  to_port           = each.value
  cidr_blocks       = ["0.0.0.0/0"]
}
```

### Python

```python
from aws_cdk import aws_ec2 as ec2, core as cdk

def make_security_group(scope, vpc):
    sg = ec2.SecurityGroup(scope, "cloud-watch-cdk", vpc=vpc, allow_all_outbound=False)
    # http
    sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80))
    # https
    sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443))

    # Parameter for my home IP address
    ssh_safe_cidr = cdk.CfnParameter(
        scope,
        "ssh-safe-cidr",
        description="The CIDR that is allowed to ssh into the instance",
    )

    ## SSH in
    sg.add_ingress_rule(ec2.Peer.ipv4(ssh_safe_cidr.value_as_string), ec2.Port.tcp(22))

    return sg
```

## IAM Role

Here again, the terraform is longer, because it doesn't have the higher level
ojbects (you'd have to write a module for it). Python implicitly creates the
instance_profile to attache the role to the ec2 instance.

### Terraform

```hcl
data "aws_iam_policy" "cloudwatch_full_access" {
  name = "CloudWatchFullAccess"
}

resource "aws_iam_role" "cloudwatch_for_ec2" {
  name = "cloudwatch_for_ec2"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "test_attach" {
  role       = aws_iam_role.cloudwatch_for_ec2.name
  policy_arn = data.aws_iam_policy.cloudwatch_full_access.arn
}

resource "aws_iam_instance_profile" "cloud_watch" {
  name = "cloud_watch"
  role = aws_iam_role.cloudwatch_for_ec2.name
}
```

### Python

```python
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
```