output "vpc_id" {
  description = "Identifier of the created VPC."
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs."
  value       = module.network.public_subnet_ids
}

output "eks_cluster_endpoint" {
  description = "Endpoint URL for the EKS cluster."
  value       = module.eks_cluster.cluster_endpoint
}

output "eks_cluster_certificate" {
  description = "Certificate authority data for the EKS cluster."
  value       = module.eks_cluster.cluster_certificate_authority
}

output "bastion_public_ip" {
  description = "Public IP of the bastion host."
  value       = try(module.bastion[0].public_ip, null)
}

