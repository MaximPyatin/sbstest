output "cluster_name" {
  description = "Name of the EKS cluster."
  value       = aws_eks_cluster.this.name
}

output "cluster_arn" {
  description = "ARN of the EKS cluster."
  value       = aws_eks_cluster.this.arn
}

output "cluster_endpoint" {
  description = "Endpoint of the EKS cluster."
  value       = aws_eks_cluster.this.endpoint
}

output "cluster_certificate_authority" {
  description = "Cluster certificate authority data."
  value       = aws_eks_cluster.this.certificate_authority[0].data
}

output "node_role_arn" {
  description = "IAM role ARN used by worker nodes."
  value       = aws_iam_role.node_group.arn
}


