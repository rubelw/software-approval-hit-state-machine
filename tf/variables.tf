variable "bucket_name" {
  type    = string
  default = "cve-bucket-xxxx"
}

variable "software_bucket_name" {
  type    = string
  default = "software-bucket-xxxxx"
}

variable "output_bucket_name" {
  type    = string
  default = "output-bucket-xxxx"
}


variable "account" {
  type    = string
  default = "xxxx"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "hosted_zone" {
  type    = string
  default = "xxxx"
}

variable "sender" {
  type    = string
  default = "admin@xxxx"
}

variable "table_name" {
  type    = string
  default = "example-table"
}

variable "approved_table_name" {
  type    = string
  default = "approved-cves"
}

variable "stage_name" {
  type    = string
  default = "test"
}