import json
import os

# Paths
BIO_PATH = os.path.join('core', 'players', 'player_bio.json')
ROSTERS_PATH = os.path.join('core', 'teams', 'data', 'rosters', 'rosters.json')
INFO_PATH = os.path.join('core', 'teams', 'data', 'player_info.json')

# Load data
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

bios = load_json(BIO_PATH)
rosters = load_json(ROSTERS_PATH)
info = load_json(INFO_PATH)

# Get all rostered player names
roster_names = set()
for team, players in rosters.items():
    for p in players:
        roster_names.add(p.strip())

# Get all player_info names
info_names = set(p['name'] for p in info)

# Get all bios names
bio_names = set(p['name'] for p in bios if isinstance(p, dict) and 'name' in p)

# Find free agents: in info but not on any roster
free_agents = []
for p in info:
    if p['name'] not in roster_names:
        free_agents.append(p)

# Also add bios with team '?' or 'Free Agent' or not in any roster
for p in bios:
    if isinstance(p, dict) and ('team' in p) and (p['team'] in ['?', 'Free Agent', '', None] or p['name'] not in roster_names):
        if p['name'] not in [fa['name'] for fa in free_agents]:
            free_agents.append(p)

# Remove duplicates by name
seen = set()
unique_free_agents = []
for p in free_agents:
    if p['name'] not in seen:
        unique_free_agents.append(p)
        seen.add(p['name'])

# Main bios: only those on a team roster
main_bios = [p for p in bios if isinstance(p, dict) and p.get('name') in roster_names]

# New structure: list of bios + free_agents section
output = {
    'players': main_bios,
    'free_agents': unique_free_agents
}

save_json(BIO_PATH, output)
print(f"Updated {BIO_PATH} with {len(main_bios)} rostered players and {len(unique_free_agents)} free agents.")
