
resource "aws_dynamodb_table" "example" {
  name           = var.table_name
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "token"
  range_key      = "ttl"

  attribute {
    name = "token"
    type = "S"
  }

  attribute {
    name = "ttl"
    type = "N"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name        = "example-table"
    Environment = "development"
  }
}


resource "aws_dynamodb_table" "approved_cves" {
  name           = "approved-cves"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "cve"
  range_key      = "ttl"

  attribute {
    name = "token"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }


  attribute {
    name = "cve"
    type = "S"
  }

  attribute {
    name = "vendor"
    type = "S"
  }

  attribute {
    name = "software"
    type = "S"
  }

  attribute {
    name = "requestor"
    type = "S"
  }

  attribute {
    name = "approver"
    type = "S"
  }

  attribute {
    name = "ttl"
    type = "N"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  global_secondary_index {
    name            = "StatusIndex"
    hash_key        = "status"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }


  global_secondary_index {
    name            = "TokenIndex"
    hash_key        = "token"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "VendorIndex"
    hash_key        = "vendor"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "SoftwareIndex"
    hash_key        = "software"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "RequestorIndex"
    hash_key        = "requestor"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  global_secondary_index {
    name            = "ApproverIndex"
    hash_key        = "approver"
    projection_type = "ALL"
    read_capacity   = 5
    write_capacity  = 5
  }

  tags = {
    Name        = "approved-cves"
    Environment = "development"
  }
}
