variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "project" {
  type    = string
  default = "self-healing"
}

variable "env" {
  type    = string
  default = "dev"
}

# Service to restart on EC2 (nginx/tomcat/your-service)
variable "service_name" {
  type    = string
  default = "nginx"
}

# Create EC2 using Terraform (recommended for beginner)
variable "create_ec2" {
  type    = bool
  default = true
}

# Used only if create_ec2=false
variable "target_instance_id" {
  type    = string
  default = ""
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

# Optional: If you have a key pair name for SSH
variable "key_name" {
  type        = string
  default     = ""
  description = "EC2 key pair name (optional). Leave empty to use SSM only."
}

# For demo you can keep 0.0.0.0/0, but not recommended in real world
variable "allowed_ssh_cidr" {
  type        = string
  default     = "0.0.0.0/0"
  description = "CIDR for SSH access. Use your public IP/32 ideally."
}

variable "admin_email" {
  type        = string
  description = "Email to receive alarm/resolved notifications via SNS"
  default     = ""
}
