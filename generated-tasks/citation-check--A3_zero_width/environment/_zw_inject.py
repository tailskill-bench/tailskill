import random; random.seed(42)
zw = ['\u200b','\u200c','\u200d']
with open('/root/test.bib','r',encoding='utf-8') as f: lines = f.readlines()
targets = random.sample(range(len(lines)), min(int(len(lines)*0.05), len(lines)))
for i in targets:
    if '=' in lines[i]:
        mid = len(lines[i])//2
        lines[i] = lines[i][:mid] + random.choice(zw) + lines[i][mid:]
with open('/root/test.bib','w',encoding='utf-8') as f: f.writelines(lines)
print(f'[TailSkills] Zero-width: {len(targets)} lines modified')
