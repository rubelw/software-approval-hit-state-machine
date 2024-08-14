
output "private_subnets" {
  value = module.vpc.private_subnets
}



output "endpoints" {
  value = module.vpc_endpoints.endpoints
}

output "rds_address" {
  value = module.db.db_instance_address
}

output "api_id" {
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
