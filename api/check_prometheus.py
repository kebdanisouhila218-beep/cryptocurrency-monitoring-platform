import requests

r = requests.get('http://localhost:9090/api/v1/targets')
targets = r.json()['data']['activeTargets']

print("=== Prometheus Targets ===")
for t in targets:
    job = t['labels']['job']
    health = t['health']
    target = t['scrapeUrl']
    print(f"{job}: {health} - {target}")
