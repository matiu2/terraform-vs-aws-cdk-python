locals {
  // Amazon Linux in pacific-south-east2
  ami_id  = "ami-0186908e2fdeea8f3"
  my_cidr = "${data.external.icanhazip_com.result.ip}/32"
}

data "external" "icanhazip_com" {
  // CIDR block of machine running the script to grant access to the security group
  program = ["curl", "https://api.ipify.org?format=json"]
}

// Security group

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

// SSH Key (just load it from "~/.ssh/id_rsa.pub")

variable "ssh-public-key-file" {
  description = "The path to your ssh public key file"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

resource "aws_key_pair" "lab-key" {
  key_name   = "cloud_lab_key"
  public_key = file(var.ssh-public-key-file)
}

// Instance

resource "aws_instance" "sysops_study" {
  ami                         = local.ami_id
  instance_type               = "t2.micro"
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.cloud_watch.id
  user_data                   = file("bootstrap.sh")
  security_groups             = [aws_security_group.cloud_watch.name]
  key_name                    = aws_key_pair.lab-key.key_name
  tags = {
    Name = "sysops_study"
  }
}


output "instance_dns_name" {
  value = aws_instance.sysops_study.public_dns
}
