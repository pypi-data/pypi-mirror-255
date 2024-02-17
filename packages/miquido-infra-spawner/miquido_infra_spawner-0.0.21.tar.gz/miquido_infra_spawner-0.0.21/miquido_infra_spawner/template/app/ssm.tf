resource "aws_ssm_parameter" "service_secrets" {
  for_each = var.ecs_service_settings.secrets
  name  = "/${var.project}/${var.environment}/${each.key}"
  type  = "SecureString"
  value = each.value
}

resource "aws_secretsmanager_secret" "gitlab" {
  name = "${var.project}/${var.environment}-gitlab"
  recovery_window_in_days = 0

}

resource "aws_secretsmanager_secret_version" "gitlab" {
  secret_id     = aws_secretsmanager_secret.gitlab.id
  secret_string = jsonencode({
     "username" : "token",
     "password" : var.gitlab_registry_token
})
}