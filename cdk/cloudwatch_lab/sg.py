"""Makes the security group"""

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
