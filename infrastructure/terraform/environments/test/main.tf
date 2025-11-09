terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

locals {
  name_prefix = var.name_prefix
  tags = merge(
    {
      Environment = "test"
      Project     = "sbs"
    },
    var.tags
  )
}

module "network" {
  source = "../../modules/network"

  name               = local.name_prefix
  cidr_block         = var.vpc_cidr
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
  availability_zones = var.availability_zones
  enable_nat_gateway = var.enable_nat_gateway
  tags               = local.tags
}

module "eks_cluster" {
  source = "../../modules/kubernetes_cluster"

  name                 = "${local.name_prefix}-eks"
  kubernetes_version   = var.kubernetes_version
  vpc_id               = module.network.vpc_id
  subnet_ids           = concat(module.network.public_subnet_ids, module.network.private_subnet_ids)
  private_subnet_ids   = module.network.private_subnet_ids
  service_ipv4_cidr    = var.service_ipv4_cidr
  endpoint_private_access = var.eks_endpoint_private_access
  endpoint_public_access  = var.eks_endpoint_public_access
  node_instance_types     = var.eks_node_instance_types
  node_capacity_type      = var.eks_node_capacity_type
  node_desired_capacity   = var.eks_node_desired_capacity
  node_min_size           = var.eks_node_min_size
  node_max_size           = var.eks_node_max_size
  node_role_additional_policies = var.eks_node_role_additional_policies
  tags = local.tags
}

module "bastion" {
  source = "../../modules/virtual_machine"

  count                 = var.create_bastion ? 1 : 0
  name                  = "${local.name_prefix}-bastion"
  vpc_id                = module.network.vpc_id
  subnet_id             = module.network.public_subnet_ids[0]
  ami_id                = var.bastion_ami_id
  instance_type         = var.bastion_instance_type
  key_name              = var.bastion_key_name
  associate_public_ip   = true
  ssh_cidr_blocks       = var.bastion_ssh_cidr_blocks
  user_data             = var.bastion_user_data
  iam_instance_profile  = var.bastion_iam_instance_profile
  tags                  = local.tags
}


