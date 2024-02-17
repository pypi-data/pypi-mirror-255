data aws_s3_bucket monitoring_bucket {
  bucket = var.miquido_monitoring_bucket
}

resource "aws_s3_object" "config" {
  bucket                 = data.aws_s3_bucket.monitoring_bucket.id
  key                    = "${var.project}-${var.environment}.yml"
  server_side_encryption = "AES256"
  content = <<EOT
- targets:
  - screeb-probe-warsaw.cleverapps.io:_:http_2xx:_:Warsaw:_:${var.gchat_webhook}:_:${local.ecs_service_domain}
EOT

}
