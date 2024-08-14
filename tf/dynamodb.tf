
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

