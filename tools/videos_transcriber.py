import os
import json
import whisper
import torch
from pathlib import Path

class Transcriber:
    def __init__(self):
        # Determine device for Whisper model
        if torch.cuda.is_available():
            self.device = "cuda"
            print("Usando GPU (CUDA) para transcrição.")
        elif torch.backends.mps.is_available():
            self.device = "mps"
            print("Usando GPU (MPS) para transcrição.")
        else:
            self.device = "cpu"
            print("Usando CPU para transcrição.")

        self.model = whisper.load_model("tiny", device=self.device) # Changed to 'tiny' for better compatibility if 'turbo' was a custom alias
        self.audios_folder = str(Path('./audios').absolute())
        self.output_name = str(Path('./transcription/transcription.json').absolute()) # Added .json extension for clarity

    def transribe(self, progress_callback=None, cancel_check_callback=None, cource_name=None):
        transcricoes = []
        
        # Get list of MP3 files to transcribe
        mp3_files = [f for f in os.listdir(self.audios_folder) if f.endswith(".mp3")]
        total_files = len(mp3_files)

        if total_files == 0:
            print("Nenhum arquivo MP3 encontrado para transcrever.")
            if progress_callback:
                progress_callback(0, 0, 100, "Nenhum arquivo.") # Signal 100% completion with 0 files
            return

        for idx, arquivo in enumerate(mp3_files):
            if cancel_check_callback and cancel_check_callback():
                print(f"Cancelamento solicitado. Interrompendo transcrição.")
                break # Exit the loop if cancellation is requested

            caminho_completo = os.path.join(self.audios_folder, arquivo)
            tmp_name = arquivo.split('.')
            name = tmp_name[0]
            try:
                # Alterado o texto conforme solicitado
                print("Transcrevendo...") 
                
                # Transcreve o áudio
                result = self.model.transcribe(caminho_completo)
                transcricoes.append({"topic": name, "transcription": result["text"]})
                print(f"Transcrição concluída para {name}.")

            except Exception as e:
                print(f"Erro ao processar {name}: {e}")
                transcricoes.append({"topic": name, "transcription": f"ERRO: {e}"}) # Add error to transcription output
            finally:
                # Always call progress_callback even if there's an error for that file
                if progress_callback:
                    progress_percentage = ((idx + 1) / total_files) * 100
                    progress_callback(idx + 1, total_files, progress_percentage, arquivo)

        # Salva as transcrições em um arquivo JSON
        with open(self.output_name, "w", encoding="utf-8") as f:
            json.dump(transcricoes, f, ensure_ascii=False, indent=4)
        print(f"Transcrições salvas em {self.output_name}.")


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
# if __name__ == "__main__":
#     diretorio_entrada = "./audios"
#     arquivo_saida = "videos.json"
#     transcrever_audios_whisper(diretorio_entrada, arquivo_saida)
