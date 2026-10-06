terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1" # Mumbai Region
}

# Fetch latest Ubuntu 24.04 LTS AMI automatically
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical owner ID

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# AWS Security Group for Flask App & SSH Access
resource "aws_security_group" "asdd_sg" {
  name        = "asdd-devops-sg"
  description = "Allow SSH, HTTP and Flask App Port 5000"

  # SSH Access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Flask Web App Access
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Standard HTTP Access
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Egress - All Outbound Traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "ASDD-Security-Group"
  }
}

# AWS EC2 Instance Resource Provisioning
resource "aws_instance" "asdd_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "t3.micro"
  key_name               = "asdd-key"
  vpc_security_group_ids = [aws_security_group.asdd_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              apt update -y
              apt install -y docker.io git
              systemctl start docker
              systemctl enable docker
              usermod -aG docker ubuntu
              EOF

  tags = {
    Name        = "ASDD-DevOps-Server"
    Environment = "MiniProject"
    Project     = "ASDD"
  }
}