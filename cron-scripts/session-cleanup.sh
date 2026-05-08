#!/bin/bash
# Session cleanup: removes done/unknown sessions older than 24h
cd /root/.openclaw/agents/main/sessions
python3 -c "
import json, os, sys

for agent_dir in ['/root/.openclaw/agents/main/sessions', '/root/.openclaw/agents/product/sessions', '/root/.openclaw/agents/engineering/sessions', '/root/.openclaw/agents/secretary/sessions']:
    sf = os.path.join(agent_dir, 'sessions.json')
    if not os.path.exists(sf):
        continue
    with open(sf, 'r') as f:
        sessions = json.load(f)
    now = int(sys.argv[1]) if len(sys.argv) > 1 else 1777426000000
    removed = 0
    for k in list(sessions.keys()):
        s = sessions[k]
        status = s.get('status', '')
        updated = s.get('updatedAt', 0)
        age_hours = (now - updated) / 3600000 if updated else 999
        if (status == 'done' and age_hours > 24) or (status == 'unknown' and age_hours > 24):
            sf_file = s.get('sessionFile', '')
            if sf_file and os.path.exists(sf_file):
                os.remove(sf_file)
                removed += 1
            del sessions[k]
    if removed > 0:
        with open(sf, 'w') as f:
            json.dump(sessions, f)
        print(f'{agent_dir}: removed {removed}')
" $1
