output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.app_server.public_ip
}

output "fastapi_docs_url" {
  description = "FastAPI Swagger Docs URL"
  value       = "http://${aws_instance.app_server.public_ip}:8000/docs"
}

output "api_base_url" {
  description = "API base URL"
  value       = "http://${aws_instance.app_server.public_ip}:8000"
}