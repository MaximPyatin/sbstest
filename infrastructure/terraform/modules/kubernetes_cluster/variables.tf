variable "name" {
  description = "Name of the EKS cluster."
  type        = string
}

variable "kubernetes_version" {
  description = "Desired Kubernetes version."
  type        = string
  default     = "1.30"
}

variable "vpc_id" {
  description = "ID of the VPC where the cluster will be created."
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs (public and private) for the control plane."
  type        = list(string)
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for node groups."
  type        = list(string)
}

variable "service_ipv4_cidr" {
  description = "Kubernetes service CIDR."
  type        = string
  default     = "172.20.0.0/16"
}

variable "endpoint_private_access" {
  description = "Enable private endpoint access."
  type        = bool
  default     = false
}

variable "endpoint_public_access" {
  description = "Enable public endpoint access."
  type        = bool
  default     = true
}

variable "node_instance_types" {
  description = "EC2 instance types for worker nodes."
  type        = list(string)
  default     = ["t3.large"]
}

variable "node_capacity_type" {
  description = "Capacity type (ON_DEMAND or SPOT)."
  type        = string
  default     = "ON_DEMAND"
}

variable "node_desired_capacity" {
  description = "Desired number of worker nodes."
  type        = number
  default     = 2
}

variable "node_min_size" {
  description = "Minimum number of worker nodes."
  type        = number
  default     = 1
}

variable "node_max_size" {
  description = "Maximum number of worker nodes."
  type        = number
  default     = 4
}

variable "node_role_additional_policies" {
  description = "Additional IAM policies to attach to the worker node role."
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "Tags applied to all resources."
  type        = map(string)
  default     = {}
}

