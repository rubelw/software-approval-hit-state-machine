variable "bucket_name" {
  type    = string
  default = "cve-bucket-xxx"
}

variable "software_bucket_name" {
  type    = string
  default = "software-bucket-xxx"
}

variable "output_bucket_name" {
  type    = string
  default = "output-bucket-xxx"
}


variable "account" {
  type    = string
  default = "xxx"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "hosted_zone" {
  type    = string
  default = "xxx"
}

variable "sender" {
  type    = string
  default = "admin@xxx"
}

variable "table_name" {
  type    = string
  default = "example-table"
}

variable "approved_table_name" {
  type    = string
  default = "approved-cves"
}

variable "requested_table_name" {
  type    = string
  default = "requested-cves"
}

variable "stage_name" {
  type    = string
  default = "test"
}

variable "key_name" {
  type = string
  default = "id_rsa"
}

variable "random_suffix" {
  type        = bool
  default     = true
  description = "Add random suffix"
}

variable "random_string_length" {
  type        = number
  default     = 3
  description = "Random string length"
}

variable "ssm_sg_name" {
  type        = string
  default     = "ssm-instance-role"
  description = "SSM instance role name"
}

variable "ingress_cidr_blocks" {
  type        = list(any)
  default     = ["10.0.0.0/16"]
  description = "List of CIDR blocks to be allowed for ingress"
}

# when using custom_ingress_cidrs, local.rfc1918 will be ignored
variable "custom_ingress_cidrs" {
  description = "List of IP addreses/network to be allowed in the ingress security group"
  type        = list(string)
  default     = null # sample ["1.2.3.4/32"] or ["1.2.3.4/32", "10.0.0.0/8"]
}

# Boolean to enable
variable "private_dns_enabled" {
  description = "Boolean to associate a private hosted zone with the specified VPC"
  type        = bool
  default     = true
}


variable "mycidr" {
  description = "cidr for deployer to access rds instance with null resource"
  type = string
  default = "50.81.152.209/32"
}

variable "enable_dynamodb_endpoint" {
  description = "Should be true if you want to provision a DynamoDB endpoint to the VPC"
  default     = false
}

variable "enable_s3_endpoint" {
  description = "Should be true if you want to provision an S3 endpoint to the VPC"
  default     = false
}

variable "enable_ssm_endpoint" {
  description = "Should be true if you want to provision an SSM endpoint to the VPC"
  default     = false
}

variable "ssm_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for SSM endpoint"
  default     = []
}

variable "ssm_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for SSM endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  default     = []
}

variable "ssm_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for SSM endpoint"
  default     = false
}

variable "enable_ssmmessages_endpoint" {
  description = "Should be true if you want to provision a SSMMESSAGES endpoint to the VPC"
  default     = false
}

variable "ssmmessages_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for SSMMESSAGES endpoint"
  default     = []
}

variable "ssmmessages_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for SSMMESSAGES endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  default     = []
}

variable "ssmmessages_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for SSMMESSAGES endpoint"
  default     = false
}

variable "enable_ec2_endpoint" {
  description = "Should be true if you want to provision an EC2 endpoint to the VPC"
  default     = false
}

variable "ec2_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for EC2 endpoint"
  default     = []
}

variable "ec2_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for EC2 endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  default     = []
}

variable "ec2_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for EC2 endpoint"
  default     = false
}

variable "enable_ec2messages_endpoint" {
  description = "Should be true if you want to provision an EC2 messages endpoint to the VPC"
  default     = false
}

variable "ec2messages_endpoint_security_group_ids" {
  description = "The ID of one or more security groups to associate with the network interface for EC2 messages endpoint"
  default     = []
}

variable "ec2messages_endpoint_subnet_ids" {
  description = "The ID of one or more subnets in which to create a network interface for EC2 messages endpoint. Only a single subnet within an AZ is supported. If omitted, private subnets will be used."
  default     = []
}

variable "ec2messages_endpoint_private_dns_enabled" {
  description = "Whether or not to associate a private hosted zone with the specified VPC for EC2 messages endpoint"
  default     = false
}

variable "rds_password" {
  type = string
  default = "adminpassword"
}