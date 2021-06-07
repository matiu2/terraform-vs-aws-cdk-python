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
