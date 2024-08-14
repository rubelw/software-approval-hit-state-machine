# IAM Role for Glue Crawler
resource "aws_iam_role" "glue_crawler_role" {
  name = "glue-crawler-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

# Attach policy to the IAM Role
resource "aws_iam_role_policy" "glue_crawler_policy" {
  name = "glue-crawler-policy"
  role = aws_iam_role.glue_crawler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:s3:::${var.bucket_name}",
          "arn:aws:s3:::${var.bucket_name}/*",
          "arn:aws:s3:::${var.software_bucket_name}",
          "arn:aws:s3:::${var.software_bucket_name}/*"
        ]
      },
      {
        Action = [
          "glue:CreateTable",
          "glue:UpdateTable",
          "glue:BatchCreatePartition",
          "glue:BatchDeletePartition",
          "glue:GetTable",
          "glue:GetTableVersion",
          "glue:GetTableVersions",
          "glue:GetPartitions",
          "glue:GetDatabase"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:glue:us-east-1:${var.account}:catalog",
          "arn:aws:glue:us-east-1:${var.account}:database/*",
          "arn:aws:glue:us-east-1:${var.account}:table/*/*"
        ]
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:AssociateKmsKey"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:logs:us-east-1:${var.account}:log-group*:/aws-glue/crawlers:log-stream:*"
        ]
      }
    ]
  })
}


resource "aws_glue_classifier" "cve" {
  name = "cve"

  csv_classifier {
    allow_single_column    = false
    contains_header        = "PRESENT"
    delimiter              = ","
    disable_value_trimming = false

    header = [
      "cvdID",
      "vendorProject",
      "product",
      "vulnerabilityName",
      "dateAdded",
      "shortDescription",
      "requiredAction",
      "dueDate",
      "knownRansomwareCampaignUse",
      "notes",
      "cwes"
    ]
    quote_symbol = "'"
  }
}

resource "aws_glue_classifier" "software" {
  name = "software"

  csv_classifier {
    allow_single_column    = false
    contains_header        = "PRESENT"
    delimiter              = ","
    disable_value_trimming = false

    header = [
      "ProductManufacturer",
      "ProductFamily",
      "ManufacturerPartNumber",
      "ProductDescription",
      "GSAScheduleContractNumber",
      "NASASEWPContractNumber",
      "ContractHolder",
      "ProductType",
      "ManageAssetManagement",
      "ManageIdentityandAccessManagement",
      "ManageNetworkSecurityManagement",
      "ManageDataProtection",
      "ProductSpecificCapability2",
      "ProductSpecificCapability3"
    ]
    quote_symbol = "'"
  }
}


resource "aws_glue_crawler" "cve_crawler" {
  name = "cve-crawler"

  classifiers = [aws_glue_classifier.cve.name]
  role        = aws_iam_role.glue_crawler_role.arn

  database_name = "cve-database" # Glue Data Catalog database
  description   = "A sample Glue Crawler"

  #s3_target {
  #  path = "s3://${var.bucket_name}/"
  #}

  catalog_target {
    database_name = aws_glue_catalog_database.cve_db.name
    tables        = [aws_glue_catalog_table.cve_table.name]
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "LOG"
  }

  # Optional - frequency for crawling
  #schedule = "cron(*/10 * * * ? *)"

}

resource "aws_glue_crawler" "software_crawler" {
  name = "software-crawler"

  role        = aws_iam_role.glue_crawler_role.arn
  classifiers = [aws_glue_classifier.software.name]

  database_name = "software-database" # Glue Data Catalog database
  description   = "A sample Glue Crawler"

  catalog_target {
    database_name = aws_glue_catalog_database.software_db.name
    tables        = [aws_glue_catalog_table.software_table.name]
  }

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "LOG"
  }

  # Optional - frequency for crawling
  #schedule = "cron(*/10 * * * ? *)"

  # Optional - other targets like JDBC, DynamoDB, etc.
}





resource "aws_glue_catalog_database" "cve_db" {
  name = "cve-database"
}

resource "aws_glue_catalog_database" "software_db" {
  name = "software-database"
}

resource "aws_glue_catalog_table" "cve_table" {
  name          = "cve_table"
  database_name = aws_glue_catalog_database.cve_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    "classification" = "csv"
  }

  storage_descriptor {
    location          = "s3://${var.bucket_name}/"
    input_format      = "org.apache.hadoop.mapred.TextInputFormat"
    output_format     = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"
    compressed        = false
    number_of_buckets = -1
    ser_de_info {
      name                  = "example_serde"
      serialization_library = "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"
      parameters = {
        "field.delim" = ","
      }
    }
    parameters = {
      EXTERNAL = "TRUE"
    }

    columns {
      name = "cvdID"
      type = "string"
    }
    columns {
      name = "vendorProject"
      type = "string"
    }
    columns {
      name = "product"
      type = "string"
    }
    columns {
      name = "vulnerabilityName"
      type = "string"
    }
    columns {
      name = "dateAdded"
      type = "string"
    }
    columns {
      name = "shortDescription"
      type = "string"
    }
    columns {
      name = "requiredAction"
      type = "string"
    }
    columns {
      name = "dueDate"
      type = "string"
    }
    columns {
      name = "knownRansomwareCampaignUse"
      type = "string"
    }
    columns {
      name = "notes"
      type = "string"
    }
    columns {
      name = "cwes"
      type = "array<STRUCT<type:string>>"
    }
  }
}


resource "aws_glue_catalog_table" "software_table" {
  name          = "software_table"
  database_name = aws_glue_catalog_database.software_db.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    "classification" = "csv"
  }

  storage_descriptor {
    location          = "s3://${var.bucket_name}/"
    input_format      = "org.apache.hadoop.mapred.TextInputFormat"
    output_format     = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"
    compressed        = false
    number_of_buckets = -1
    ser_de_info {
      name                  = "example_serde"
      serialization_library = "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"
      parameters = {
        "field.delim" = ","
      }
    }
    parameters = {
      EXTERNAL = "TRUE"
    }


    columns {
      name = "ProductManufacturer"
      type = "string"
    }
    columns {
      name = "ProductFamily"
      type = "string"
    }
    columns {
      name = "ManufacturerPartNumber"
      type = "string"
    }
    columns {
      name = "ProductDescription"
      type = "string"
    }
    columns {
      name = "GSAScheduleContractNumber"
      type = "string"
    }
    columns {
      name = "NASASEWPContractNumber"
      type = "string"
    }
    columns {
      name = "ContractHolder"
      type = "string"
    }
    columns {
      name = "ProductType"
      type = "string"
    }
    columns {
      name = "ManageAssetManagement"
      type = "string"
    }
    columns {
      name = "ManageIdentityandAccessManagement"
      type = "string"
    }
    columns {
      name = "ManageNetworkSecurityManagement"
      type = "string"
    }
    columns {
      name = "ManageDataProtection"
      type = "string"
    }
    columns {
      name = "ProductSpecificCapability2"
      type = "string"
    }
    columns {
      name = "ProductSpecificCapability3"
      type = "string"
    }
  }
}