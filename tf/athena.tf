resource "aws_athena_workgroup" "example" {
  name = "example-workgroup"
  configuration {
    result_configuration {
      output_location = "s3://${var.output_bucket_name}/"
    }
  }
}