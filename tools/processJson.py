import json
import re
from pathlib import Path

class JsonProcessor:
    def __init__(self, file_to_process_path: Path, database_file: Path):
        self.file_to_process = str(file_to_process_path.absolute())
        self.database_file = str(database_file.absolute())

    def split_transcription(self, transcription: str) -> list:
        """
        Divide uma transcrição em chunks baseado em limite de caracteres
        e pontuação de término.
        """
        buffer = ""
        chunks = []

        for char in transcription:
            buffer += char

            if len(buffer) >= 350 and char in {'.', '!', '?'}:
                chunks.append(buffer.strip())
                buffer = ""

        if buffer:
            chunks.append(buffer.strip())

        return chunks

    def process_contents(self, data: list) -> list:
        """
        Processa o conteúdo: divide transcrições em chunks,
        agrupa em uma lista de content para cada item e preserva a URL/ID.
        """
        new_contents = []

        for item in data:
            file_name = item.get("file_name")
            course = item.get("course")
            topic = item.get("topic")
            image = item.get("image")
            # Captura a URL ou ID processado no método process
            video_url = item.get("video_url", "") 
            transcription = item.get("transcription", "")

            transcription_chunks = self.split_transcription(transcription)

            # Estrutura Hierárquica Intermediária
            # Prepara os dados para o formato que put_in_db espera ler
            contents_list = []
            seq = 1
            
            # Adiciona vídeo se houver
            if video_url:
                contents_list.append({
                    "type_content": "video",
                    "content": video_url,
                    "topic_reference": topic,
                    "sequence": seq
                })
                seq += 1
            
            # Adiciona transcrições
            for chunk in transcription_chunks:
                contents_list.append({
                    "type_content": "transcription",
                    "content": chunk,
                    "topic_reference": topic,
                    "sequence": seq
                })
                seq += 1

            new_contents.append({
                "course": {
                    "name": course,
                    "img": image
                },
                "topic": {
                    "name": topic,
                    # A sequência será recalculada corretamente no put_in_db
                    "sequence": 0, 
                    "course_reference": course
                },
                "contents": contents_list,
                "file_name": file_name # Mantém referência se necessário
            })

        return new_contents

    def process(self, video_urls: list = None) -> list:
        """
        Carrega o arquivo cru, insere URLs, estrutura os dados hierarquicamente
        e salva no transcription.json.
        """
        try:
            with open(self.file_to_process, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if video_urls:
                for i, item in enumerate(data):
                    if i < len(video_urls):
                        raw_url = video_urls[i]
                        # REGEX: Captura ID do Youtube (v=ID)
                        match = re.search(r"v=([^&]+)", raw_url)
                        if match:
                            item['video_url'] = match.group(1).strip()
                        else:
                            item['video_url'] = raw_url
                    else:
                        item['video_url'] = ""

            # Processa e gera a estrutura hierárquica
            processed_data = self.process_contents(data)

            # Salva o arquivo intermediário transcription.json
            with open(str(self.file_to_process), 'w', encoding='utf-8') as file:
                json.dump(processed_data, file, ensure_ascii=False, indent=4)

            print(f"Dados processados e salvos em {self.file_to_process}")
            return processed_data
            
        except Exception as e:
            print(f"Erro ao processar JSON: {e}")
            raise e
    
    def put_in_db(self):
        """
        Lê o transcription.json (hierárquico), lê o data.json (relacional),
        mescla os dados garantindo sequências únicas e salva no data.json.
        """
        try:
            # 1. Carregar dados novos (transcription.json)
            with open(self.file_to_process, 'r', encoding='utf-8') as file:
                new_items = json.load(file)

            # 2. Carregar banco de dados atual (data.json)
            db_data = {"courses": [], "topics": [], "contents": []}
            if Path(self.database_file).exists():
                try:
                    with open(self.database_file, 'r', encoding='utf-8') as file:
                        db_data = json.load(file)
                except json.JSONDecodeError:
                    print("Banco de dados vazio ou corrompido, criando novo.")

            # 3. Determinar a última sequência de Tópicos para continuar a numeração
            last_topic_sequence = 0
            if db_data["topics"]:
                # Pega o maior número de sequência existente
                last_topic_sequence = max(t.get("sequence", 0) for t in db_data["topics"])

            # 4. Iterar sobre os novos itens e adicionar ao DB
            for item in new_items:
                # --- COURSE ---
                # Verifica se o curso já existe para não duplicar
                new_course = item.get('course')
                course_exists = False
                for db_course in db_data['courses']:
                    if db_course['name'] == new_course['name']:
                        course_exists = True
                        break
                
                if not course_exists:
                    db_data['courses'].append(new_course)

                # --- TOPIC ---
                # Incrementa a sequência global baseada no banco de dados
                last_topic_sequence += 1
                
                new_topic = item.get('topic')
                # Atualiza a sequência do tópico novo
                new_topic['sequence'] = last_topic_sequence
                
                db_data['topics'].append(new_topic)

                # --- CONTENTS ---
                # Adiciona todos os conteúdos (vídeo e textos)
                # A sequência interna do conteúdo já veio pronta do process_contents (1, 2, 3...)
                new_contents = item.get('contents', [])
                db_data['contents'].extend(new_contents)

            # 5. Salvar o banco de dados atualizado
            with open(self.database_file, 'w', encoding='utf-8') as file:
                json.dump(db_data, file, ensure_ascii=False, indent=4)

            print(f"Banco de dados atualizado com sucesso em: {self.database_file}")
            print(f"Novos tópicos adicionados. Sequência parou em: {last_topic_sequence}")

        except Exception as e:
            print(f"Erro ao inserir no banco de dados: {e}")
            raise e