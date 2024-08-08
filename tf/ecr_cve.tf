# Force deletion configuration
resource "null_resource" "delete_ecr_cve" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr delete-repository --repository-name ${aws_ecr_repository.my_repository_cve.name} --force
    EOT
  }

  depends_on = [aws_ecr_repository.my_repository_cve]
}

resource "aws_ecr_repository" "my_repository_cve" {
  name                 = "my-cve_ecr-repo" # Replace with your desired repository name
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = "MyCveECRRepository"
    Environment = "Production"
  }
  provisioner "local-exec" {
    command = <<EOT
      # Log in to ECR
      aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${aws_ecr_repository.my_repository_cve.repository_url}

      # Tag the Docker image
      docker tag my_custom_cve_image:latest ${aws_ecr_repository.my_repository_cve.repository_url}:latest

      # Push the Docker image to ECR
      docker push ${aws_ecr_repository.my_repository_cve.repository_url}:latest
    EOT
  }
}

resource "aws_ecr_repository_policy" "my_cve_repository_policy" {
  repository = aws_ecr_repository.my_repository_cve.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
      }
    ]
  })
}