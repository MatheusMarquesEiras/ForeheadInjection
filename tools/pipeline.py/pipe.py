import yt_dlp
import os
import json
import whisper
import torch
from queue import Queue
import uuid
import random

from dataclasses import dataclass

@dataclass
class Course:
    name: str
    img: str

    def to_dict(self):
        return {'name': self.name, 'img': self.img}
    
    def get_name(self):
        return self.name
    
@dataclass
class Topic:
    name: str
    sequence: int
    course_reference: str

    def to_dict(self):
        return {'name': self.name, 'sequence': self.sequence, 'course_reference': self.course_reference}
    
@dataclass
class Content:
    type_content: str
    content: str
    topic_reference: str
    sequence: int

    def to_dict(self):
        return {'type_content': self.type_content, 'content': self.content, 'topic_reference': self.topic_reference, 'sequence': self.sequence}


class Pipe:
    def __init__(
                self,
                _audios_folder: str = './audios',
                _transcriptions_file: str = './transcriptions.json',
                ):
        
        self._audios_folder = _audios_folder
        self._transcriptions_file = _transcriptions_file
        self._device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self._course: Course
        self._topics: Queue[Topic] = Queue()
        self._contents: Queue[Content] = Queue()
        self._urls: Queue[str] = Queue()
    
    def _split_transcription(self, transcription: str, name):
        buffer = ""
        idx = 2

        for char in transcription:
            buffer += char

            if len(buffer) >= 350 and char in {'.', '!', '?'}:
                self._contents.put(Content(type_content='transcription', content=buffer, topic_reference=name, sequence=idx))
                buffer = ""
                idx += 1

        if buffer:
            self._contents.put(Content(type_content='transcription', content=buffer, topic_reference=name, sequence=idx))
    
    def download_audio(self, video_urls: list[str]):
        """
        Allow download videos from a list of ULR or download a playlist at once
        """
        options = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self._audios_folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            for url in video_urls:
                try:
                    print(f"Baixando: {url}")
                    ydl.download([url])
                    self._urls.put(url.replace('https://www.youtube.com/watch?v=', ''))
                except Exception as e:
                    print(f"Erro ao baixar {url}: {e}")

    def transcribe(self):
        print("Carregando o modelo Whisper...")
        model = whisper.load_model("turbo", device=self._device)
        transcricoes = []

        for file in os.listdir(self._audios_folder):
            if file.endswith(".mp3"):
                full_path = os.path.join(self._audios_folder, file)
                try:
                    print(f"Transcrevendo {file}...")
                    result = model.transcribe(full_path)
                    transcricoes.append({"name": file, "transcription": result["text"], "uuid": str(uuid.uuid4())})
                    print(f"Transcrição concluída para {file}.")
                except Exception as e:
                    print(f"Erro ao processar {file}: {e}")

        with open(self._transcriptions_file, "w", encoding="utf-8") as f:
            json.dump(transcricoes, f, ensure_ascii=False, indent=4)
        print(f"Transcrições salvas em {self._transcriptions_file}.")

    def process_transcription(self):
        with open(self._transcriptions_file, 'r',  encoding="utf-8") as f:
            data = json.load(f)

        for idx, obj in enumerate(data):
            self._contents.put(Content(type_content='video', content=self._urls.get(), topic_reference=obj['name'], sequence=1))
            self._split_transcription(obj['transcription'], obj['name'])
            self._topics.put(Topic(name=obj['name'], sequence=idx + 1, course_reference=obj['uuid']))
            self._course = Course(name=obj['uuid'], img=random.randint(1, 100))

    def create_json(self):
        data = {
            "course": self._course.to_dict(),
            "topics": [],
            "contents": []
        }

        while not self._topics.empty():
            topic = self._topics.get()
            data["topics"].append(topic.to_dict())

        while not self._contents.empty():
            content = self._contents.get()
            data["contents"].append(content.to_dict())

        with open('finish.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    p = Pipe()
    p.download_audio(video_urls=['https://www.youtube.com/watch?v=0XFq9K7N9o4'])
    p.transcribe()
    p.process_transcription()
    p.create_json()