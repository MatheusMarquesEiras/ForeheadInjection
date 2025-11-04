import os
import json
import whisper
import torch
from pathlib import Path

class Transcriber:
    def __init__(self):
        self.model = whisper.load_model("turbo", device="cuda")
        self.audios_folder = str(Path('./audios').absolute())
        self.output_name = str(Path('./transcription').absolute())

    def transribe(self):
        transcricoes = []
        for arquivo in os.listdir(diretorio_entrada):
            if arquivo.endswith(".mp3"):
                caminho_completo = os.path.join(diretorio_entrada, arquivo)
                try:
                    print(f"Transcrevendo {arquivo}...")
                    # Transcreve o áudio
                    result = self.model.transcribe(caminho_completo)
                    transcricoes.append({"nome": arquivo, "transcrito": result["text"]})
                    print(f"Transcrição concluída para {arquivo}.")
                except Exception as e:
                    print(f"Erro ao processar {arquivo}: {e}")

        # Salva as transcrições em um arquivo JSON
        with open(arquivo_saida, "w", encoding="utf-8") as f:
            json.dump(transcricoes, f, ensure_ascii=False, indent=4)
        print(f"Transcrições salvas em {arquivo_saida}.")

def transcrever_audios_whisper(diretorio_entrada, arquivo_saida):
    """
    Transcreve arquivos de áudio em um diretório e salva as transcrições em um arquivo JSON.
    
    Args:
        diretorio_entrada (str): Caminho para o diretório contendo os arquivos de áudio.
        arquivo_saida (str): Caminho para o arquivo JSON de saída.
    """
    # Verifica se a GPU está disponível
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA não está disponível. Certifique-se de ter uma GPU compatível e o PyTorch configurado corretamente.")

    # Carrega o modelo Whisper na GPU
    print("Carregando o modelo Whisper...")
    model = whisper.load_model("turbo", device="cuda")

    # Lista para armazenar as transcrições
    transcricoes = []

    # Itera sobre os arquivos no diretório
    for arquivo in os.listdir(diretorio_entrada):
        if arquivo.endswith(".mp3"):
            caminho_completo = os.path.join(diretorio_entrada, arquivo)
            try:
                print(f"Transcrevendo {arquivo}...")
                # Transcreve o áudio
                result = model.transcribe(caminho_completo)
                transcricoes.append({"nome": arquivo, "transcrito": result["text"]})
                print(f"Transcrição concluída para {arquivo}.")
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")

    # Salva as transcrições em um arquivo JSON
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        json.dump(transcricoes, f, ensure_ascii=False, indent=4)
    print(f"Transcrições salvas em {arquivo_saida}.")

# Exemplo de uso
if __name__ == "__main__":
    diretorio_entrada = "./audios"
    arquivo_saida = "videos.json"
    transcrever_audios_whisper(diretorio_entrada, arquivo_saida)
