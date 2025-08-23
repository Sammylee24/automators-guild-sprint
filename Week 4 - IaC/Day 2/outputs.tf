# outputs.tf

output "web_server_public_ip" {
  description = "The public IP address of the Web Server"
  value       = aws_instance.web_server.public_ip
}

output "ssh_command" {
  description = "Command to SSH into the Web Server"
  value       = "ssh -i ${var.key_name}.pem ec2-user@${aws_instance.web_server.public_ip}"
}