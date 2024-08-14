resource "aws_cloudwatch_event_rule" "every_ten_minutes" {
  name                = "every_ten_minutes_rule"
  schedule_expression = "rate(10 minutes)"
}

resource "aws_cloudwatch_event_rule" "every_5_minutes" {
  name        = "every_5_minutes_rule"
  description = "trigger lambda every 5 minute"

  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "lambda1_target" {
  rule      = aws_cloudwatch_event_rule.every_ten_minutes.name
  target_id = "SendToLambda"
  arn       = aws_lambda_function.lambda_function_1.arn
}

