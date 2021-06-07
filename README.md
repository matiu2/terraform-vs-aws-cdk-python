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
