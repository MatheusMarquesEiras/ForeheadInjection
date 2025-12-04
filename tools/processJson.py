import json
from pathlib import Path

class JsonProcessor:
    def __init__(self, file_to_process_path: Path):
        self.file_to_process = str(file_to_process_path.absolute())

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
        Processa o conteúdo: divide transcrições em chunks
        e agrupa em uma lista de content para cada item.
        """
        new_contents = []

        for item in data:
            file_name = item.get("file_name")
            course = item.get("course")
            topic = item.get("topic")
            image = item.get("image")
            transcription = item.get("transcription", "")

            transcription_chunks = self.split_transcription(transcription)

            new_contents.append({
                "course": course,
                "topic": topic,
                "content": transcription_chunks,
                "image": image,
                "file_name": file_name
            })

        return new_contents

    def process(self) -> list:
        """
        Carrega o arquivo JSON, processa o conteúdo
        e salva em um novo arquivo.
        """
        with open(self.file_to_process, 'r', encoding='utf-8') as file:
            data = json.load(file)

        processed_data = self.process_contents(data)

        with open(str(self.file_to_process), 'w', encoding='utf-8') as file:
            json.dump(processed_data, file, ensure_ascii=False, indent=4)

        print(f"Data processed and saved to {self.file_to_process}")
        print(f"Total items: {len(processed_data)}")

        return processed_data
    
    def put_in_db(self):
        pass
        # with open(str(self.file_to_process), 'w', encoding='utf-8') as file:
        #     data = json.load(file)

        # dict_data_processed = {'courses': [], 'topics': [], 'contents': []}
        # cource = {'name': '', 'img': ''}
        # topic = {"name": '', "sequence": 0, "course_reference": ""}
        # content = {"type_content": "", "content": "", "topic_reference": "", "sequence": 0}

        # for item in data:
        #     cource["name"] = item['course']
        #     cource['img'] = item['image']

        #     topic


# if __name__ == "__main__":
#     processor = JsonProcessor(Path('./transcription/transcription.json'))
#     processor.process()