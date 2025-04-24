import json
import pandas as pd
from pathlib import Path

relative_path = Path('./backend')

data_file = relative_path / 'data.json'

# Carregar o JSON do arquivo
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

courses = 'courses'
topics = 'topics'
contents = 'contents'

# Criar DataFrames
df_courses = pd.DataFrame(data[courses])
df_topics = pd.DataFrame(data[topics])
df_contents = pd.DataFrame(data[contents])

# Salvar o arquivo com a chave externa "courses"

def write_individual_json(name, data: json):
    file_path = relative_path / f'df_{name}.json'

    with open(file_path.absolute(), 'w', encoding='utf-8') as file:
        json.dump({f"{name}": data.to_dict(orient='records')}, file, ensure_ascii=False, indent=2)

write_individual_json(courses, df_courses)
write_individual_json(topics, df_topics)
write_individual_json(contents, df_contents)

"""
with open('df_courses.json', 'w', encoding='utf-8') as file:
    json.dump({"courses": df_courses.to_dict(orient='records')}, file, ensure_ascii=False, indent=2)

with open('df_topics.json', 'w', encoding='utf-8') as file:
    json.dump({"topics": df_topics.to_dict(orient='records')}, file, ensure_ascii=False, indent=2)

with open('df_contents.json', 'w', encoding='utf-8') as file:
    json.dump({"contents": df_contents.to_dict(orient='records')}, file, ensure_ascii=False, indent=2)
"""