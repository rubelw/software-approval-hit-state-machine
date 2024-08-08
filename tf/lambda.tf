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
