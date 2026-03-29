#!/bin/bash
# deploy.sh — Setup JRVC Node on Hetzner VPS (Ubuntu 22.04)
# Run as root: bash deploy.sh

set -e

echo "=== JRVC Node Deployment ==="

# 1. System update
apt-get update -y && apt-get upgrade -y

# 2. Install Docker
apt-get install -y docker.io docker-compose curl
systemctl enable docker
systemctl start docker

# 3. Clone repo
git clone https://github.com/jrvc-network/ail-lang.git /opt/jrvc
cd /opt/jrvc

# 4. Build & run
docker build -f jrvc_blockchain/Dockerfile -t jrvc-node ./jrvc_blockchain
docker run -d \
  --name jrvc-node \
  --restart always \
  -p 80:8080 \
  jrvc-node

echo ""
echo "=== Node is live ==="
echo "REST API : http://$(curl -s ifconfig.me)/"
echo "WebSocket: ws://$(curl -s ifconfig.me)/ws/YOUR_AGENT_ID"
echo "Docs     : http://$(curl -s ifconfig.me)/docs"
