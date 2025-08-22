resource "aws_security_group" "web_app_sg" {
  name        = "web_app_sg"
  description = "Web Application Security Group"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web_app_sg"
  }
}

resource "aws_instance" "web_app_instance" {
  ami = var.ami
  subnet_id = data.aws_subnet.default.id
  vpc_security_group_ids = [aws_security_group.web_app_sg.id]
  instance_type = var.instance_type
  tags = {
    Name = "web-app"
  }
}