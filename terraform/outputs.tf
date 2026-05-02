output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.flask_app.repository_url
}

output "eks_cluster_name" {
  description = "Name of the EKS cluster"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "Endpoint for EKS cluster"
  value       = aws_eks_cluster.main.endpoint
}