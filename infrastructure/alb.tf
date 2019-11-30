// ALB Security Group.
resource "aws_security_group" "alb" {
  name        = "${var.name}-alb-sg"
  description = "${var.name_readable} ALB access security group."
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.alb_ingress_cidrs
  }

  egress {
    from_port = "0"
    to_port   = "0"
    protocol  = "-1"
    cidr_blocks = [
      "0.0.0.0/0"
    ]
  }

  tags = {
    Name = "${var.name}-alb-sg"
  }
}

resource "aws_alb" "main" {
  name            = "${var.name}-ecs-alb"
  subnets         = aws_subnet.public.*.id
  security_groups = [aws_security_group.alb.id]

  tags = {
    Name = "${var.name}-ecs-alb"
  }
}

resource "aws_alb_target_group" "ecs" {
  name     = "${var.name}-ecs-target-group"
  port     = "80"
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path = "/admin/login/"
  }

  tags = {
    Name = "${var.name}-ecs-target-group"
  }
}

resource "aws_alb_listener" "http_listener" {
  load_balancer_arn = aws_alb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_alb_target_group.ecs.arn
    type             = "forward"
  }
}
