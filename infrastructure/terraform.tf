terraform {
  backend "s3" {
    bucket = "health-log-state"
    key    = "state/terraform.tfstate"
    region = "us-east-1"
  }
}