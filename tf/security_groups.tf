resource "aws_security_group" "ec2_sg" {
  vpc_id =module.vpc.vpc_id


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "TLS from VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "TLS from VPC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks =  ["0.0.0.0/0"]

  }
}

resource "aws_security_group" "ssm" {

  name_prefix = "vpc-endpoint-ssm-"
  description = "SSM VPC Endpoint Security Group"
  vpc_id      = module.vpc.vpc_id
}

resource "aws_security_group_rule" "vpc_endpoint_ssm_https" {

  cidr_blocks       = [local.vpc_cidr]
  type              = "ingress"
  protocol          = "tcp"
  from_port         = 443
  to_port           = 443
  security_group_id = "${aws_security_group.ssm.id}"
}

resource "aws_security_group" "ssmmessages" {

  name_prefix = "vpc-endpoint-ssm-messages-"
  description = "SSM MESSAGES VPC Endpoint Security Group"
  vpc_id      =  module.vpc.vpc_id
}

resource "aws_security_group_rule" "vpc_endpoint_ssm_messages_https" {

  cidr_blocks       = [local.vpc_cidr]
  type              = "ingress"
  protocol          = "tcp"
  from_port         = 443
  to_port           = 443
  security_group_id = "${aws_security_group.ssmmessages.id}"
}

resource "aws_security_group" "ec2" {

  name_prefix = "vpc-endpoint-ec2-"
  description = "EC2 VPC Endpoint Security Group"
  vpc_id      =  module.vpc.vpc_id
}

resource "aws_security_group_rule" "vpc_endpoint_ec2_https" {

  cidr_blocks       = [local.vpc_cidr]
  type              = "ingress"
  protocol          = "tcp"
  from_port         = 443
  to_port           = 443
  security_group_id = "${aws_security_group.ec2.id}"
}


resource "aws_security_group" "ec2messages" {

  name_prefix = "vpc-endpoint-ec2-messages-"
  description = "EC2 MESSAGES VPC Endpoint Security Group"
  vpc_id      =  module.vpc.vpc_id
}

resource "aws_security_group_rule" "vpc_endpoint_ec2_messages_https" {

  cidr_blocks       = [local.vpc_cidr]
  type              = "ingress"
  protocol          = "tcp"
  from_port         = 443
  to_port           = 443
  security_group_id = "${aws_security_group.ec2messages.id}"
}


# Security Group for Lambda
resource "aws_security_group" "lambda_sg" {
  vpc_id = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
