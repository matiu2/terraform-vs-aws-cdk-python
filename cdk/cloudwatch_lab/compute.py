from aws_cdk import aws_ec2 as ec2, core as cdk


def make_ec2_instance(scope, role, vpc, sg):
    image = ec2.LookupMachineImage(name="amzn2-ami-hvm-2.0.20210427.0-x86_64-ebs")
    instance_type = ec2.InstanceType("t2.micro")

    # Parameters
    key_pair_name = cdk.CfnParameter(
        scope,
        "ssh-key-pair-name",
    )

    user_data_param = cdk.CfnParameter(
        scope,
        "user-data",
    )

    # user_data
    user_data = ec2.UserData.for_linux()
    user_data.add_commands(user_data_param.value_as_string)

    return ec2.Instance(
        scope,
        "cloud-watch",
        instance_type=instance_type,
        machine_image=image,
        role=role,
        vpc=vpc,
        key_name=key_pair_name.value_as_string,
        user_data=user_data,
        security_group=sg,
    )
