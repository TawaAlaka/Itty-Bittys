resource "random_string" "db_password" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_ssm_parameter" "app_db_password" {
  name        = "/${var.name}/database/password"
  description = "${var.name_readable} database master password."
  type        = "SecureString"
  value       = random_string.db_password.result

  lifecycle {
    ignore_changes = [value]
  }
}

resource "aws_security_group" "app_db" {
  name        = "${var.name}-db-sg"
  description = "Controls access to the application database."
  vpc_id      = aws_vpc.main.id

  tags = {
    Name = "${var.name}-db-sg"
  }

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_instance.id]
  }
}

resource "aws_db_subnet_group" "app_db_subnet_group" {
  name       = "${var.name}-db-subnet-group"
  subnet_ids = aws_subnet.public.*.id

  tags = {
    Name = "${var.name}-db-subnet-group"
  }
}


resource "aws_db_instance" "default" {
  identifier             = "${var.name}-database"
  allocated_storage      = 5
  engine                 = "postgres"
  engine_version         = "11.5"
  instance_class         = "db.t2.micro"
  multi_az               = false
  name                   = var.name
  username               = var.name
  password               = aws_ssm_parameter.app_db_password.value
  db_subnet_group_name   = aws_db_subnet_group.app_db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.ecs_instance.id]
  skip_final_snapshot    = true

  tags = {
    Name = "${var.name}-db"
  }

  lifecycle {
    ignore_changes = [password]
  }
}
