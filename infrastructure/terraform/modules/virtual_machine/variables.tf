variable "name" {
  description = "Name of the virtual machine."
  type        = string
}

variable "vpc_id" {
  description = "VPC identifier."
  type        = string
}

variable "subnet_id" {
  description = "Subnet identifier."
  type        = string
}

variable "ami_id" {
  description = "AMI identifier to use for the instance."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Key pair name for SSH access."
  type        = string
  default     = null
}

variable "associate_public_ip" {
  description = "Associate a public IP with the instance."
  type        = bool
  default     = true
}

variable "ssh_cidr_blocks" {
  description = "CIDR blocks allowed to access SSH."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "user_data" {
  description = "User data script."
  type        = string
  default     = null
}

variable "iam_instance_profile" {
  description = "IAM instance profile to attach."
  type        = string
  default     = null
}

variable "tags" {
  description = "Resource tags."
  type        = map(string)
  default     = {}
}

