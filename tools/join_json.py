import json
from pathlib import Path

base_path = Path('./tools/json')

a1 = base_path / 'df_contents.json'
a2 = base_path / 'df_courses.json'
a3 = base_path / 'df_topics.json'

output_file = base_path / 'df_unificado.json'

with a2.open(encoding='utf-8') as f1, \
     a3.open(encoding='utf-8') as f2, \
     a1.open(encoding='utf-8') as f3:
    
    data1 = json.load(f1)
    data2 = json.load(f2)
    data3 = json.load(f3)

json_unificado = {**data1, **data2, **data3}

with output_file.open('w', encoding='utf-8') as file:
    json.dump(json_unificado, file, ensure_ascii=False, indent=2)
