# main.tf
provider "aws" {
  region = var.region
}

terraform {
  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.1.0" # Use the appropriate version
    }
  }
}

resource "aws_iam_role" "step_functions_role" {
  name = "StepFunctionsRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "states.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "step_functions_policy" {
  name = "StepFunctionsPolicy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "lambda:InvokeFunction",
          "lambda:InvokeAsync"
        ],
        Effect = "Allow",
        Resource = [
          aws_lambda_function.lambda_function_1.arn,
          aws_lambda_function.lambda_function_2.arn,
          aws_lambda_function.lambda_function_5.arn,
          aws_lambda_function.lambda_function_6.arn,
          aws_lambda_function.lambda_function_7.arn
        ]
      },
      {
        Action = [
          "sqs:SendMessage"
        ],
        Effect   = "Allow",
        Resource = aws_sqs_queue.example.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "step_functions_policy_attachment" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = aws_iam_policy.step_functions_policy.arn
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
  depends_on    = [aws_lambda_function.lambda_function_7, aws_sfn_state_machine.example]
  function_name = "lambda_function_6"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_function_6.lambda_handler"

  runtime = "python3.9"
  timeout = 120 # Timeout set to 120 seconds
  publish = true

  environment {
    variables = {
      STATE_MACHINE_ARN            = aws_sfn_state_machine.example.arn,
      SECOND_LAMBDA_ARN            = aws_lambda_function.lambda_function_7.arn,
      DYNAMODB_TABLE_NAME          = var.table_name,
      DYNAMODB_APPROVED_TABLE_NAME = var.approved_table_name
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

resource "aws_lambda_permission" "lambda6_invoke_lambda7" {
  statement_id  = "AllowLambda1InvokeLambda2"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function_7.function_name
  principal     = "lambda.amazonaws.com"
  source_arn    = aws_lambda_function.lambda_function_6.arn
}

resource "aws_lambda_alias" "function7" {
  name             = "lambda_function_7"
  function_name    = aws_lambda_function.lambda_function_7.function_name
  function_version = aws_lambda_function.lambda_function_7.version
}

resource "aws_lambda_function" "lambda_function_7" {
  function_name = "lambda_function_7"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_function_7.lambda_handler"

  runtime = "python3.9"
  timeout = 120 # Timeout set to 120 seconds

  filename         = "lambda_function_7_payload.zip"
  source_code_hash = filebase64sha256("lambda_function_7_payload.zip")
  publish          = true

  environment {
    variables = {
      SENDER     = var.sender,
      API_URL    = "https://${aws_api_gateway_rest_api.example_api.id}.execute-api.${var.region}.amazonaws.com/${var.stage_name}",
      TABLE_NAME = var.table_name
    }
  }
}

resource "aws_lambda_function" "lambda_function_8" {
  function_name = "lambda_function_8"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "lambda_function_8.lambda_handler"

  runtime = "python3.9"
  timeout = 120 # Timeout set to 120 seconds

  filename         = "lambda_function_8_payload.zip"
  source_code_hash = filebase64sha256("lambda_function_8_payload.zip")
  publish          = true
}

resource "aws_lambda_alias" "function8" {
  name             = "lambda_function_8"
  function_name    = aws_lambda_function.lambda_function_8.function_name
  function_version = aws_lambda_function.lambda_function_8.version
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

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = ["lambda.amazonaws.com", "apigateway.amazonaws.com"]
        }
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_exec_policy" {
  name = "lambda_exec_policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      Effect   = "Allow",
      Resource = "*"
      },
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Effect = "Allow",
        Resource = [
          "arn:aws:s3:::${var.bucket_name}",
          "arn:aws:s3:::${var.bucket_name}/*",
          "arn:aws:s3:::${var.software_bucket_name}",
          "arn:aws:s3:::${var.software_bucket_name}/*"
        ]
      },
      {
        Action = [
          "s3:*"
        ],
        Effect = "Allow",
        Resource = [
          "arn:aws:s3:::${var.output_bucket_name}",
          "arn:aws:s3:::${var.output_bucket_name}/*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ],
        "Resource" : "arn:aws:ecr:${var.region}:${var.account}:repository/my-ecr-repo"
        }, {
        "Effect" : "Allow",
        "Action" : [
          "ecr:GetAuthorizationToken"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "athena:*"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "glue:*"
        ],
        "Resource" : [
          "*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "lambda:InvokeFunction"
        ],
        "Resource" : [
          "arn:aws:lambda:${var.region}:${var.account}:function:lambda_function_5",
          "arn:aws:lambda:${var.region}:${var.account}:function:lambda_function_7",
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:ChangeMessageVisibility",
          "sqs:GetQueueAttributes" # Add this line
        ],
        Resource = aws_sqs_queue.example.arn
      },
      {
        Effect = "Allow",
        Action = [
          "states:StartExecution"
        ],
        Resource = aws_sfn_state_machine.example.arn
      },
      {
        Effect   = "Allow",
        Action   = "ses:SendEmail",
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:GetItem",
          "dynamodb:Query"
        ]
        Resource = [
          "arn:aws:dynamodb:${var.region}:${var.account}:table/${var.table_name}",
          "arn:aws:dynamodb:${var.region}:${var.account}:table/${var.approved_table_name}",
          "arn:aws:dynamodb:${var.region}:${var.account}:table/approved-cves/index/*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "states:SendTaskSuccess",
          "states:SendTaskFailure"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_exec_policy_attachment" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_exec_policy.arn
}

resource "aws_sfn_state_machine" "example" {
  name     = "example-state-machine"
  role_arn = aws_iam_role.step_functions_role.arn

  definition = jsonencode({
    Comment = "A state machine that sends a message to an SQS queue and waits for a human response",
    StartAt = "SendMessage",
    States = {
      SendMessage = {
        Type     = "Task",
        Resource = "arn:aws:states:::sqs:sendMessage.waitForTaskToken",
        Parameters = {
          QueueUrl = aws_sqs_queue.example.id,
          MessageBody = {
            "taskToken.$" = "$$.Task.Token",
            "input.$"     = "$"
          }
        },
        Next = "WaitForHuman"
      },
      WaitForHuman = {
        Type    = "Wait",
        Seconds = 7200, # Wait for up to 1 hour
        End     = true
      }
    }
  })
}

