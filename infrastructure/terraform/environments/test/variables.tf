variable "aws_region" {
  description = "AWS region to provision resources in."
  type        = string
}

variable "name_prefix" {
  description = "Prefix used to name all resources."
  type        = string
  default     = "sbs-test"
}

variable "tags" {
  description = "Additional tags to add to all resources."
  type        = map(string)
  default     = {}
}

variable "vpc_cidr" {
  description = "CIDR for the VPC."
  type        = string
  default     = "10.10.0.0/16"
}

variable "public_subnets" {
  description = "List of CIDR ranges for public subnets."
  type        = list(string)
  default     = ["10.10.0.0/24", "10.10.1.0/24"]
}

variable "private_subnets" {
  description = "List of CIDR ranges for private subnets."
  type        = list(string)
  default     = ["10.10.10.0/24", "10.10.11.0/24"]
}

variable "availability_zones" {
  description = "Availability zones to use (must match the number of subnets)."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "enable_nat_gateway" {
  description = "Whether to create a NAT Gateway."
  type        = bool
  default     = true
}

variable "service_ipv4_cidr" {
  description = "Kubernetes service IPv4 CIDR."
  type        = string
  default     = "172.20.0.0/16"
}

variable "kubernetes_version" {
  description = "Version for the Kubernetes control plane."
  type        = string
  default     = "1.30"
}

variable "eks_endpoint_private_access" {
  description = "Enable private access to the EKS endpoint."
  type        = bool
  default     = false
}

variable "eks_endpoint_public_access" {
  description = "Enable public access to the EKS endpoint."
  type        = bool
  default     = true
}

variable "eks_node_instance_types" {
  description = "Instance types for worker nodes."
  type        = list(string)
  default     = ["t3.large"]
}

variable "eks_node_capacity_type" {
  description = "Capacity type for worker nodes."
  type        = string
  default     = "ON_DEMAND"
}

variable "eks_node_desired_capacity" {
  description = "Desired number of worker nodes."
  type        = number
  default     = 2
}

variable "eks_node_min_size" {
  description = "Minimum number of worker nodes."
  type        = number
  default     = 1
}

variable "eks_node_max_size" {
  description = "Maximum number of worker nodes."
  type        = number
  default     = 4
}

variable "eks_node_role_additional_policies" {
  description = "Additional IAM policies for EKS node role."
  type        = list(string)
  default     = []
}

variable "create_bastion" {
  description = "Create a bastion host for administrative access."
  type        = bool
  default     = true
}

variable "bastion_ami_id" {
  description = "AMI ID for the bastion host."
  type        = string
}

variable "bastion_instance_type" {
  description = "Instance type for the bastion host."
  type        = string
  default     = "t3.small"
}

variable "bastion_key_name" {
  description = "SSH key name for the bastion host."
  type        = string
  default     = null
}

variable "bastion_ssh_cidr_blocks" {
  description = "CIDR blocks that can SSH into the bastion host."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "bastion_user_data" {
  description = "User data script for the bastion host."
  type        = string
  default     = null
}

variable "bastion_iam_instance_profile" {
  description = "IAM instance profile for the bastion host."
  type        = string
  default     = null
}


