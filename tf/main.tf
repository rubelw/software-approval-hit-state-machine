# main.tf
provider "aws" {
  region = var.region

  skip_credentials_validation = true
  skip_requesting_account_id  = false
  skip_metadata_api_check     = true
  skip_region_validation      = true
}


terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.1.0" # Use the appropriate version
    }
  }
}

################################################################################
# RDS Module
################################################################################
module "db" {
  source = "terraform-aws-modules/rds/aws"

  identifier = local.name

  # All available versions: http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_MySQL.html#MySQL.Concepts.VersionMgmt
  engine               = "mysql"
  engine_version       = "8.0"
  family               = "mysql8.0" # DB parameter group
  major_engine_version = "8.0"      # DB option group
  instance_class       = "db.t3.small"
  password          = "adminpassword"  # Master password
  manage_master_user_password = false


  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = "completeMysql"
  username = "admin"
  port     = 3306

  multi_az               = false
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.rds_security_group.security_group_id]

  maintenance_window              = "Mon:00:00-Mon:03:00"
  backup_window                   = "03:00-06:00"
  enabled_cloudwatch_logs_exports = ["general"]
  create_cloudwatch_log_group     = true

  skip_final_snapshot = true
  deletion_protection = false

  performance_insights_enabled          = false
  performance_insights_retention_period = 7
  create_monitoring_role                = false
  monitoring_interval                   = 0

  parameters = [
    {
      name  = "character_set_client"
      value = "utf8mb4"
    },
    {
      name  = "character_set_server"
      value = "utf8mb4"
    }
  ]

  tags = local.tags
  db_instance_tags = {
    "Sensitive" = "high"
  }
  db_option_group_tags = {
    "Sensitive" = "low"
  }
  db_parameter_group_tags = {
    "Sensitive" = "low"
  }
  db_subnet_group_tags = {
    "Sensitive" = "high"
  }
}


module "db_disabled" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "${local.name}-disabled"

  create_db_instance        = false
  create_db_parameter_group = false
  create_db_option_group    = false
}

################################################################################
# Supporting Resources
################################################################################

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = local.name
  cidr = local.vpc_cidr

  azs              = local.azs
  public_subnets   = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k)]
  private_subnets  = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 3)]
  database_subnets = [for k, v in local.azs : cidrsubnet(local.vpc_cidr, 8, k + 6)]

  create_database_subnet_group = true
  enable_nat_gateway = true
  single_nat_gateway   = true
  enable_dns_hostnames = true

  tags = local.tags
}




module "rds_security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 5.0"

  name        = local.name
  description = "Complete MySQL example security group"
  vpc_id      = module.vpc.vpc_id

  # ingress
  ingress_with_cidr_blocks = [
    {
      from_port   = 3306
      to_port     = 3306
      protocol    = "tcp"
      description = "MySQL access from within VPC"
      cidr_blocks = module.vpc.vpc_cidr_block
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 3306
      to_port     = 3306
      protocol    = "tcp"
      description = "MySQL access from within VPC"
      cidr_blocks = module.vpc.vpc_cidr_block
    }
  ]

  tags = local.tags
}





module "vpc_endpoints" {
  source = "./terraform-aws-vpc/modules/vpc-endpoints"

  vpc_id = module.vpc.vpc_id

  create_security_group      = true
  security_group_name_prefix = "${local.name}-vpc-endpoints-"
  security_group_description = "VPC endpoint security group"
  subnet_ids   = module.vpc.private_subnets

  security_group_rules = {
    ingress_https = {
      description = "HTTPS from VPC"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  endpoints = {
    s3 = {
      service             = "s3"
      private_dns_enabled = true
      dns_options = {
        private_dns_only_for_inbound_resolver_endpoint = false
      }
      tags = { Name = "s3-vpc-endpoint" }
    },

    rds = {
      service             = "rds"
      private_dns_enabled = true
    },
    ssm = {
      service   = "ssm"
      private_dns_enabled = true
    }

    ssmmessages = {
      service   = "ssmmessages"
      private_dns_enabled = true

    }

    ec2messages = {
      service   = "ec2messages"
      private_dns_enabled = true

    }
  }

  tags = merge(local.tags, {
    Project  = "Secret"
    Endpoint = "true"
  })
}
