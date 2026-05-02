terraform {
  backend "s3" {
    bucket         = "flask-devops-terraform-state-app"
    key            = "project1/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "flask-devops-terraform-locks"
    encrypt        = true
  }
}