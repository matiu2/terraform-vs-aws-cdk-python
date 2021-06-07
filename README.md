This compares terraform and aws-cdk for a small deployment.

We're building a lab for the [udemy course for AWS SysOps Associate](https://www.udemy.com/course/aws-certified-sysops-administrator-associate/learn/lecture/2691470?start=195#overview)

All we need is:

 * An EC2 instance
   + An ssh key to sign into it
   + A role that allows it to run cloudwatch operations
   + A bootstrap userdata file (you have to sign up for the couse to get it)
   + A security group allowing SSH from my house

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
 * I like the terraform code better; it's an explicit, purpose built language with strong constraints.
 * You could say "oh, but python makes things more flexible". I don't see that
   a as a plus; it gives you more chance to complicate things
 * In CDK, when creating the SecurityGroup using the high level object,
   AllowAllOutbound defaults to true if you leave it out. Great for getting
   things done, not great for security. Terraform is more explicit; you have to
   say what you want.
 * That goes without saying, that terraform is also multicloud
