#!/bin/sh
# ==================================================================
#  Project   : Neura-Nix - Multimodal AI Assistant {Ollama MultiRag}
#  Author    : UjjwalS (https://www.ujjwalsaini.dev)
#  License   : Apache-2.0
#  Copyright : © 2025 UjjwalS. All rights reserved.
# ==================================================================

set -e
echo "🚀 Starting Nginx for Neura-Nix..."
cp ./nginx/default.conf /etc/nginx/conf.d/default.conf
nginx -t
# Run in foreground (for Docker/K8s)
exec nginx -g 'daemon off;'
