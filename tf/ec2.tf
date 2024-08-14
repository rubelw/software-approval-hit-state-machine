resource "aws_instance" "mysql_server" {
  ami           = "ami-0ae8f15ae66fe8cda"  # Amazon Linux 2 AMI ID

  instance_type = "t2.small"
  key_name      = var.key_name

  subnet_id = module.vpc.private_subnets[0]

  associate_public_ip_address = false

  iam_instance_profile = aws_iam_instance_profile.ssm_instance_profile.name

  # Security group to allow MySQL traffic
  security_groups = [aws_security_group.ec2_sg.id]

  user_data = templatefile("${path.module}/setup.sh", {
    rds_address = module.db.db_instance_address,
    rds_password = var.rds_password
  })

  tags = {
    Name = "MySQL-Server"
  }
}


# Create an instance profile
resource "aws_iam_instance_profile" "ssm_instance_profile" {
  name = "ssm-instance-profile"
  role = aws_iam_role.ssm_role.name
}
