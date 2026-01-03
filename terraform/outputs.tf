output "demo_instance_id" {
  value = local.target_id
}

output "demo_instance_public_ip" {
  value = var.create_ec2 ? aws_instance.demo[0].public_ip : null
}

output "sns_topic_arn" {
  value = aws_sns_topic.alarm_topic.arn
}

output "lambda_name" {
  value = aws_lambda_function.self_heal.function_name
}
