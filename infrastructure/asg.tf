data "template_file" "launch_configuration_user_data" {
  template = file("${path.module}/resources/user_data.tpl")

  vars = {
    cluster_name = aws_ecs_cluster.application_cluster.name
  }
}

data "aws_ami" "ecs_optimized" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-2.0.????????-x86_64-ebs"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }
}

resource "aws_launch_configuration" "application" {
  security_groups = [
    aws_security_group.ecs_instance.id
  ]
  associate_public_ip_address = true
  iam_instance_profile = aws_iam_instance_profile.ecs_instance_profile.name
  image_id = data.aws_ami.ecs_optimized.id
  instance_type = "t2.micro"
  name_prefix = "${var.name}-lc-"
  user_data = data.template_file.launch_configuration_user_data.rendered

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "application" {
  name = "${var.name}-autoscaling-group"
  min_size = 2
  max_size = 2
  desired_capacity = 2
  launch_configuration = aws_launch_configuration.application.name
  target_group_arns = [aws_alb_target_group.ecs.arn]
  vpc_zone_identifier = aws_subnet.public.*.id
}
