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
                "sequence": len(transcription_chunks)
            })

        return new_contents

    def process(self, output_path: Path = None) -> list:
        """
        Carrega o arquivo JSON, processa o conteúdo
        e salva em um novo arquivo.
        """
        with open(self.file_to_process, 'r', encoding='utf-8') as file:
            data = json.load(file)

        processed_data = self.process_contents(data)

        if output_path is None:
            output_path = Path('tmp.json')

        with open(str(output_path.absolute()), 'w', encoding='utf-8') as file:
            json.dump(processed_data, file, ensure_ascii=False, indent=4)

        print(f"Data processed and saved to {output_path}")
        print(f"Total items: {len(processed_data)}")
        print(f"Total chunks in first item: {processed_data[0]['sequence']}")

        return processed_data


# if __name__ == "__main__":
#     processor = JsonProcessor(Path('./transcription/transcription.json'))
#     processor.process()