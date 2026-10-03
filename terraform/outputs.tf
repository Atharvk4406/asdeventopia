output "instance_id" {
  description = "ID of the provisioned AWS EC2 Instance"
  value       = aws_instance.asdd_server.id
}

output "public_ip" {
  description = "Public IP Address of the provisioned AWS EC2 Instance"
  value       = aws_instance.asdd_server.public_ip
}

output "instance_type" {
  description = "EC2 Instance Type"
  value       = aws_instance.asdd_server.instance_type
}

output "app_url" {
  description = "Direct Application Web URL on AWS EC2"
  value       = "http://${aws_instance.asdd_server.public_ip}:5000"
}
