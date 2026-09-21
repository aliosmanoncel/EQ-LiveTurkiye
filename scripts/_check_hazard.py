import json, numpy as np
with open('data/hazard_grid.json', encoding='utf-8') as f:
    d = json.load(f)
grid = d['grid']
pga = np.array([p['pga'] for p in grid])
print(f'Nokta: {len(grid)}')
print(f'PGA min={pga.min():.6f}  max={pga.max():.6f}  ort={pga.mean():.6f}')
print(f'PGA>0.01g: {(pga>0.01).sum()}')
print(f'PGA>0.05g: {(pga>0.05).sum()}')
for p in grid[:3]:
    print(p)
