#!/bin/sh
# ===========================================
# Neura-Nix: Multimodal Assistant
# Author: UjjwalS
# Website: https://ujjwalsaini.dev
# ===========================================

set -e
echo "🚀 Starting Nginx for Neura-Nix..."
cp ./nginx/default.conf /etc/nginx/conf.d/default.conf
nginx -t
# Run in foreground (for Docker/K8s)
exec nginx -g 'daemon off;'
