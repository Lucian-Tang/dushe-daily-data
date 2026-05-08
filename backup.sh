#!/bin/bash
cd /root/.openclaw/workspace || exit 1
git add .
git commit -m "workspace backup $(date +%Y-%m-%d_%H:%M)" || true
git push origin main 2>&1
if [ $? -eq 0 ]; then
  echo "BACKUP_OK"
else
  echo "BACKUP_FAIL"
fi
