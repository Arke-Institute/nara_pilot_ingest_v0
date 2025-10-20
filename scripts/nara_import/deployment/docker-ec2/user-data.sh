#!/bin/bash
# EC2 User Data - Install Docker only
# Everything else happens via SSH
set -e

echo "Installing Docker..."
apt-get update -qq
apt-get install -y -qq docker.io
systemctl start docker
systemctl enable docker
usermod -a -G docker ubuntu

echo "Docker installed successfully"
