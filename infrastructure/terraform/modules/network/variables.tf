variable "name" {
  description = "Prefix used for naming resources."
  type        = string
}

variable "cidr_block" {
  description = "CIDR block for the VPC."
  type        = string
}

variable "public_subnets" {
  description = "List of CIDR blocks for public subnets."
  type        = list(string)
  default     = []
}

variable "private_subnets" {
  description = "List of CIDR blocks for private subnets."
  type        = list(string)
  default     = []
}

variable "availability_zones" {
  description = "List of availability zones matching subnets."
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Whether to create a NAT Gateway for private subnets."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Common tags applied to resources."
  type        = map(string)
  default     = {}
}

