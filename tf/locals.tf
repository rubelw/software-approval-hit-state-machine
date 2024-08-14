locals {
  rfc1918       = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  ingress_cidrs = var.custom_ingress_cidrs != null ? var.custom_ingress_cidrs : local.rfc1918

  name   = "complete-mysql"
  region = "us-east-1"

  vpc_cidr = "10.0.0.0/16"
  azs      = slice(data.aws_availability_zones.available.names, 0, 3)

  tags = {
    Name       = local.name
    Example    = local.name
  }
}


