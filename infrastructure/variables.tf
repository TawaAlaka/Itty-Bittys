variable "name" {
  default     = "healthlog"
  description = "Name prefix for this environment."
}

variable "name_readable" {
  default     = "Health Log"
  description = "Human readable name for this environment."
}

variable "aws_region" {}

variable "ecr_repo_name" {}

variable "alb_ingress_cidrs" { type = list(string) }

variable "alb_admin_ingress_cidrs" { type = list(string) }

variable "public_subnet_count" { default = 2 }

variable "private_subnet_count" { default = 2 }

