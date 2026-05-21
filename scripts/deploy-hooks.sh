#!/bin/bash
# Deploy pre-push hook to .git/hooks/
cp "$(git rev-parse --show-toplevel)/scripts/pre-push.sh" "$(git rev-parse --show-toplevel)/.git/hooks/pre-push"
chmod +x "$(git rev-parse --show-toplevel)/.git/hooks/pre-push"
echo "✅ pre-push hook deployed"
