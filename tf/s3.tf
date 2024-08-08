resource "aws_s3_bucket" "example" {
  bucket        = var.bucket_name
  force_destroy = true
  acl           = "private"
}

resource "aws_s3_bucket" "software" {
  bucket        = var.software_bucket_name
  force_destroy = true
  acl           = "private"
}

resource "aws_s3_bucket" "output" {
  bucket        = var.output_bucket_name
  force_destroy = true
  acl           = "private"
}
