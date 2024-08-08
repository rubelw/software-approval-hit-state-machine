output "repository_url" {
  value = aws_ecr_repository.my_repository.repository_url
}

output "state_machine_arn" {
  value = aws_sfn_state_machine.example.arn
}

output "rest_api_id" {
  description = "REST API id"
  value       = aws_api_gateway_rest_api.example_api.id
}

output "deployment_id" {
  description = "Deployment id"
  value       = aws_api_gateway_deployment.api_gateway_deployment.id
}

output "deployment_invoke_url" {
  description = "Deployment invoke url"
  value       = aws_api_gateway_deployment.api_gateway_deployment.invoke_url
}

output "deployment_execution_arn" {
  description = "Deployment execution ARN"
  value       = aws_api_gateway_deployment.api_gateway_deployment.execution_arn
}



output "name" {
  description = "API Gateway name"
  value       = aws_api_gateway_rest_api.example_api.name
}