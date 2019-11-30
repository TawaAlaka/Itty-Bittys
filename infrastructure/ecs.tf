#### IAM ROLES ####

// ECS instance role.
resource "aws_iam_role" "ecs_instance_role" {
  name               = "${var.name}-ecs-instance-role"
  assume_role_policy = file("${path.module}/resources/assume_role_policy.json")
}

//resource "aws_iam_role_policy" "ecs_instance_role" {
//  name = "${var.name}-ecs-instance-role-policy"
//  role = aws_iam_role.ecs_instance_role.id
//  policy = file("${path.module}/resources/instance_role_policy.json")
//}

resource "aws_iam_role_policy_attachment" "ecs_instance_role_attachment" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

// ECS instance profile.
resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "${var.name}-ecs-instance-profile"
  role = aws_iam_role.ecs_instance_role.name
}

// ECS service role.
//resource "aws_iam_role" "ecs_service_role" {
//  name               = "${var.name}_ecs_service_role"
//  assume_role_policy = file("${path.module}/resources/assume_role_policy.json")
//}
//
//resource "aws_iam_role_policy" "ecs_service_role_policy" {
//  policy = file("${path.module}/resources/svc-role-policy.json")
//  role = aws_iam_role.ecs_service_role.name
//}
//resource "aws_iam_role_policy_attachment" "ecs_service_role_attachment" {
//  role       = aws_iam_role.ecs_service_role.name
//  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceRole"
//}

#### SECURITY GROUPS ####

// Security group for each instance.
resource "aws_security_group" "ecs_instance" {
  name        = "${var.name}-ecs-instance"
  vpc_id      = aws_vpc.main.id
  description = "Security group for ${var.name_readable} ECS instances."

  tags = {
    Name = "${var.name}-ecs-instances"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"

    security_groups = [
      aws_security_group.alb.id
    ]
  }
}

resource "aws_ecs_cluster" "application_cluster" {
  name = var.name
}

data "aws_ecr_repository" "application" {
  name = var.ecr_repo_name
}

resource "random_string" "app_secret" {
  length  = 24
  special = true
}

resource "aws_ssm_parameter" "app_secret" {
  name        = "/${var.name}/application/secret"
  description = "${var.name_readable} application secret."
  type        = "SecureString"
  value       = random_string.app_secret.result

  lifecycle {
    ignore_changes = [value]
  }
}

data "template_file" "task_definition" {
  template = file("${path.module}/resources/task_definition.json")

  vars = {
    task_name   = var.name
    task_image  = var.ecr_repo_name
    allowed_hosts = aws_alb.main.dns_name
    secret      = aws_ssm_parameter.app_secret.value
    db_host     = aws_db_instance.default.address
    db_port     = aws_db_instance.default.port
    db_name     = aws_db_instance.default.name
    db_user     = aws_db_instance.default.username
    db_password = aws_ssm_parameter.app_db_password.value
  }
}

resource "aws_ecs_task_definition" "application_task_definition" {
  family                = var.name
  network_mode          = "host"
  container_definitions = data.template_file.task_definition.rendered
}

resource "aws_ecs_service" "application" {
  name            = var.name
  cluster         = aws_ecs_cluster.application_cluster.id
  task_definition = aws_ecs_task_definition.application_task_definition.arn
  desired_count   = 2
//  iam_role = aws_iam_role.ecs_service_role.arn
//
//  load_balancer {
//    target_group_arn = aws_alb_target_group.ecs.arn
//    container_name   = var.name
//    container_port   = 80
//  }
}
