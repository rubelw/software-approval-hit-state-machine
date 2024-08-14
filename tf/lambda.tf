# Wait for the image to be available
resource "null_resource" "wait_for_image" {
  depends_on = [
    aws_ecr_repository.my_repository
  ]

  provisioner "local-exec" {
    command = "sleep 90" # Wait for 30 seconds
  }
}

# Wait for the image to be available
resource "null_resource" "wait_for_cve_image" {
  depends_on = [
    aws_ecr_repository.my_repository_cve
  ]

  provisioner "local-exec" {
    command = "sleep 90" # Wait for 30 seconds
  }
}



resource "aws_lambda_function" "lambda_function_5" {
  function_name = "lambda_function_5"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_function_5.lambda_handler"
  publish       = true

  runtime = "python3.9"
  timeout = 120 # Timeout set to 120 seconds

  environment {
    variables = {
      TABLE_NAME = var.table_name
    }
  }

  filename         = "lambda_function_5_payload.zip"
  source_code_hash = filebase64sha256("lambda_function_5_payload.zip")
}

resource "aws_lambda_alias" "function5" {
  name             = "lambda_function_5"
  function_name    = aws_lambda_function.lambda_function_5.function_name
  function_version = aws_lambda_function.lambda_function_5.version
}

resource "aws_lambda_function" "lambda_function_6" {
  depends_on = [module.db]

  function_name = "lambda_function_6"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_function_6.lambda_handler"

  vpc_config {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [aws_security_group.lambda_sg.id]
  }

  runtime = "python3.9"
  timeout = 120 # Timeout set to 120 seconds
  publish = true

  environment {
    variables = {
      DB_HOST = module.db.db_instance_address
      DB_USER = "admin"
      DB_PASSWORD = var.rds_password
      DB_NAME = "db"
      DYNAMODB_TABLE_NAME          = var.table_name,
      SENDER     = var.sender,
      API_URL    = "https://${aws_api_gateway_rest_api.example_api.id}.execute-api.${var.region}.amazonaws.com/${var.stage_name}",
    }
  }

  filename         = "lambda_function_6_payload.zip"
  source_code_hash = filebase64sha256("lambda_function_6_payload.zip")
}

resource "aws_lambda_alias" "function6" {
  name             = "lambda_function_6"
  function_name    = aws_lambda_function.lambda_function_6.function_name
  function_version = aws_lambda_function.lambda_function_6.version
}

resource "aws_lambda_function" "lambda_function_1" {
  depends_on = [
    aws_ecr_repository.my_repository_cve,
    null_resource.wait_for_cve_image
  ]
  function_name = "lambda_function_1"
  role          = aws_iam_role.lambda_exec_role.arn
  image_uri     = "${var.account}.dkr.ecr.${var.region}.amazonaws.com/my-cve_ecr-repo:latest"
  package_type  = "Image"
  timeout       = 620
  memory_size   = 1024
  publish       = true
}

resource "aws_lambda_permission" "allow_eventbridge1" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function_1.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_5_minutes.arn
}

resource "aws_lambda_function" "lambda_function_2" {
  depends_on = [
    aws_ecr_repository.my_repository,
    null_resource.wait_for_image
  ]
  function_name = "lambda_function_2"
  role          = aws_iam_role.lambda_exec_role.arn

  image_uri    = "${var.account}.dkr.ecr.${var.region}.amazonaws.com/my-ecr-repo:latest"
  package_type = "Image"
  timeout      = 620
  memory_size  = 1024
  publish      = true
}
