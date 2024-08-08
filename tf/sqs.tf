resource "aws_sqs_queue" "example" {
  name                       = "example-queue"
  visibility_timeout_seconds = 120 # Set this to match or exceed the Lambda function timeout

}



resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowSQSTrigger"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_function_7.function_name
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.example.arn
}

resource "aws_lambda_event_source_mapping" "sqs_to_lambda" {
  event_source_arn = aws_sqs_queue.example.arn
  function_name    = aws_lambda_function.lambda_function_7.arn
  enabled          = true
  batch_size       = 10
}

