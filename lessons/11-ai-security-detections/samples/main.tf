# Source-only preview fixture. Do not apply.
# count = 0 keeps the intentionally insecure resource inert.
resource "aws_security_group" "preview_only" {
  count = 0
  name  = "ai-detection-preview-only"

  ingress {
    description = "Intentionally broad SSH access for detection training"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
