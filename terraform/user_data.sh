#!/bin/bash
set -euxo pipefail

yum update -y
yum install -y git docker

systemctl enable docker
systemctl start docker

usermod -aG docker ec2-user

# Install Docker Compose v2 manually
mkdir -p /usr/local/lib/docker/cli-plugins

curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose

chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

docker compose version

cd /home/ec2-user

if [ ! -d "Insurance-policy-FastAPI" ]; then
  git clone ${repo_url}
fi

cd Insurance-policy-FastAPI

docker compose down || true
docker compose up -d --build