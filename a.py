import json
from pathlib import Path

class TranscriptionProcessor:
    def __init__(self):
        self.transcriptio_file = str(Path('./transcription/transcription.json').absolute())

    def process(self):
        with open(self.transcriptio_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for content in data:
            content['transcription'] = self._process_transcription(content['transcription'])

        
        with open(str(Path('./transcription/tmp.json').absolute()), 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    
    def _process_transcription(self, content):
        buffer = ''
        splited_transcription = []

        for char in content:
            buffer += char

            if len(buffer) >= 350 and char in {'.', '!', '?'}:
                splited_transcription.append(buffer.strip())
                buffer = ""

        if buffer:
            splited_transcription.append(buffer.strip())
        
        return splited_transcription


if __name__ == "__main__":
    tra = TranscriptionProcessor()
    tra.process()