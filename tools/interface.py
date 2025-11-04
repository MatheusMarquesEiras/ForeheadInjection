import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from videos_transcriber import Transcriber

import yt_dlp

# ========================== Função de download (baseada no seu exemplo) ==========================

def baixar_videos_para_audio(video_urls, pasta_destino, progress_callback=None, finished_callback=None, error_callback=None):
    """
    Baixa vídeos do YouTube e converte para áudio em formato MP3.

    Args:
        video_urls (list): Lista de URLs dos vídeos do YouTube.
        pasta_destino (str): Caminho da pasta onde os arquivos serão salvos.
        progress_callback (callable): Hook de progresso do yt_dlp (opcional).
        finished_callback (callable): Chamado quando tudo terminar sem exceções (opcional).
        error_callback (callable): Chamado em caso de exceção (opcional).
    """
    os.makedirs(pasta_destino, exist_ok=True)

    opcoes = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(pasta_destino, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],

        # Workaround para o problema de "Only images are available" / SABR:
        'extractor_args': {
            'youtube': {
                # Você pode tentar ['android', 'tv'] se necessário
                'player_client': ['android']
            }
        },

        # Robustez
        'retries': 10,
        'fragment_retries': 10,
        'ignoreerrors': True,
        'noplaylist': True,
        'concurrent_fragment_downloads': 1,

        # Progresso
        'progress_hooks': [progress_callback] if progress_callback else []
    }

    try:
        ydl_instance = yt_dlp.YoutubeDL(opcoes)
        # Execute download for each URL separately to allow better cancellation checks
        for url in video_urls:
            # yt_dlp does not have a direct way to cancel an ongoing download via hooks
            # The _cancel_flag in main.py will be checked *between* downloads/transcriptions
            ydl_instance.download([url])

        if finished_callback:
            finished_callback()

    except Exception as e:
        if error_callback:
            error_callback(e)


# ========================== Interface Tkinter ==========================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Baixar áudio do YouTube (MP3) e Transcrever")
        self.root.geometry("800x550")
        self.root.minsize(700, 500)

        self.destino = str(Path('./audios').absolute())

        self.trancriber = Transcriber()

        self._build_ui()
        self._set_idle_state()

        # Controle de cancelamento
        self._cancel_flag = False

    # ----------- Construção da UI -----------
    def _build_ui(self):
        titulo = tk.Label(self.root, text="Baixar áudio do YouTube (MP3) e Transcrever", font=("Arial", 20, "bold"))
        titulo.pack(pady=15)

        frame_url = tk.Frame(self.root)
        frame_url.pack(fill="x", padx=20)

        lbl_url = tk.Label(frame_url, text="URLs (uma por linha):", font=("Arial", 12, "bold"))
        lbl_url.pack(anchor="w")

        self.txt_urls = tk.Text(frame_url, height=1, font=("Consolas", 11))
        self.txt_urls.pack(fill="both", expand=True, pady=8)

        frame_prog = tk.Frame(self.root)
        frame_prog.pack(fill="x", padx=20, pady=(10, 0))

        lbl_download_bar = tk.Label(frame_prog, text="Progresso do Download:", font=("Arial", 10))
        lbl_download_bar.pack(anchor="w")
        self.download_bar = ttk.Progressbar(frame_prog, orient="horizontal", length=400, mode="determinate", maximum=100)
        self.download_bar.pack(fill="x")

        lbl_transcriber_bar = tk.Label(frame_prog, text="Progresso da Transcrição:", font=("Arial", 10))
        lbl_transcriber_bar.pack(anchor="w", pady=(8,0))
        self.transcriber_bar = ttk.Progressbar(frame_prog, orient="horizontal", length=400, mode="determinate", maximum=100)
        self.transcriber_bar.pack(fill="x", pady=(0, 8))

        self.lbl_status = tk.Label(self.root, text="Aguardando...", font=("Arial", 12))
        self.lbl_status.pack(pady=8)

        frame_acoes = tk.Frame(self.root)
        frame_acoes.pack(pady=10)

        self.btn_baixar = tk.Button(frame_acoes, text="Iniciar", command=self._iniciar_processo, font=("Arial", 12), width=12)
        self.btn_baixar.grid(row=0, column=0, padx=5)

        self.btn_cancelar = tk.Button(frame_acoes, text="Cancelar", command=self._cancelar, font=("Arial", 12), width=12, state="disabled")
        self.btn_cancelar.grid(row=0, column=1, padx=5)

    # ----------- Estado de UI -----------
    def _set_busy_state(self):
        self.btn_baixar.config(state="disabled")
        self.btn_cancelar.config(state="normal")
        self.txt_urls.config(state="disabled")

    def _set_idle_state(self):
        self.btn_baixar.config(state="normal")
        self.btn_cancelar.config(state="disabled")
        self.txt_urls.config(state="normal")
        self._set_progress(0, "download")
        self._set_progress(0, "transcriber")
        self._set_status("Aguardando...")
        self._cancel_flag = False # Reset cancel flag when idle

    # ----------- Helpers de UI (sempre thread principal) -----------
    def _set_status(self, texto):
        self.lbl_status.config(text=texto)

    def _set_progress(self, percent, bar_type="download"):
        p = max(0.0, min(100.0, float(percent)))
        if bar_type == "download":
            if str(self.download_bar.cget("mode")) == "indeterminate":
                self.download_bar.stop()
                self.download_bar.config(mode="determinate")
            self.download_bar['value'] = p
        elif bar_type == "transcriber":
            self.transcriber_bar['value'] = p

    def _start_indeterminate(self):
        self.download_bar.config(mode="indeterminate")
        self.download_bar.start(15)

    def _stop_indeterminate(self):
        if str(self.download_bar.cget("mode")) == "indeterminate":
            self.download_bar.stop()
            self.download_bar.config(mode="determinate")
            self.download_bar['value'] = 0

    # New callback for transcriber progress
    def _transcriber_progress_callback(self, current, total, percentage, filename):
        if self._cancel_flag:
            # If cancellation is requested, stop updating UI but the transcription for current file will complete.
            # The loop in Transcriber.transcribe should break if it receives True from a cancel_check_callback.
            return
        p = max(0.0, min(100.0, float(percentage)))
        self.root.after(0, self._set_progress, p, "transcriber")
        self.root.after(0, self._set_status, f"Transcrevendo... {current} de {total} ({p:.1f}%) - {filename}")

    # ----------- Botões -----------
    def _iniciar_processo(self):
        urls_raw = self.txt_urls.get("1.0", "end").strip()
        if not urls_raw:
            messagebox.showwarning("Atenção", "Informe ao menos uma URL (uma por linha).")
            return

        urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]

        self._cancel_flag = False
        self._set_busy_state()
        self._set_status("Preparando downloads...")
        self._set_progress(0, "download")
        self._set_progress(0, "transcriber")

        # Inicia thread de trabalho
        th = threading.Thread(target=self._worker_process, args=(urls, self.destino), daemon=True)
        th.start()

    def _cancelar(self):
        self._cancel_flag = True
        self.root.after(0, self._set_status, "Cancelando processo...")
        self.btn_cancelar.config(state="disabled") # Disable cancel button after it's pressed

    # ----------- Worker em thread separada -----------
    def _worker_process(self, urls, pasta_destino):
        # Hook de progresso para download
        def download_progress_hook(d):
            # Check cancellation flag, though yt_dlp doesn't have an interruptible hook.
            # This check primarily stops further files from being downloaded if multiple URLs are provided.
            if self._cancel_flag:
                # Signify that a cancellation was requested, but current download might finish.
                return

            status = d.get('status')
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            baixado = d.get('downloaded_bytes')
            speed = d.get('speed')
            eta = d.get('eta')

            if status == 'downloading':
                if total and baixado:
                    percent = (baixado / total) * 100.0
                    self.root.after(0, self._set_progress, percent, "download")
                    msg = f"Baixando... {percent:.1f}%"
                    if speed:
                        msg += f" | Vel: {speed/1024/1024:.2f} MB/s"
                    if eta:
                        msg += f" | ETA: {eta}s"
                    self.root.after(0, self._set_status, msg)
                else:
                    self.root.after(0, self._set_status, "Baixando... (tamanho total desconhecido)")
                    self.root.after(0, self._start_indeterminate)

            elif status == 'finished':
                self.root.after(0, self._stop_indeterminate)
                self.root.after(0, self._set_progress, 100, "download")
                self.root.after(0, self._set_status, "Download concluído! Convertendo/Finalizando...")

        # Função de callback para quando o download terminar com sucesso
        def on_download_finished_successfully():
            if self._cancel_flag:
                self.root.after(0, self._set_status, "Processo cancelado após downloads.")
                self.root.after(0, self._set_idle_state)
                return

            self.root.after(0, self._set_status, "Download concluído! Iniciando transcrição...")
            self.root.after(0, lambda: self.transcriber_bar.config(value=0)) # Reset transcriber bar

            try:
                # Start transcription phase
                self.trancriber.transribe(progress_callback=self._transcriber_progress_callback, cancel_check_callback=lambda: self._cancel_flag)
                self.root.after(0, self._set_status, "Transcrições concluídas!")
                self.root.after(0, self._set_progress, 100, "transcriber")
                self.root.after(0, self._set_idle_state)
            except Exception as e:
                self.root.after(0, self._set_status, "Erro durante a transcrição.")
                self.root.after(0, self._set_progress, 0, "transcriber") # Reset on error
                self.root.after(0, self._set_idle_state)
                self.root.after(0, lambda: messagebox.showerror("Erro na Transcrição", f"Ocorreu um erro durante a transcrição:\n{e}"))

        # Função de callback para erros gerais
        def on_process_error(e, phase="Geral"):
            self.root.after(0, self._stop_indeterminate)
            self.root.after(0, self._set_status, f"Erro durante o processo ({phase}).")
            self.root.after(0, self._set_idle_state)
            self.root.after(0, lambda: self.download_bar.config(value=0))
            self.root.after(0, lambda: self.transcriber_bar.config(value=0))
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Ocorreu um erro na fase de {phase}:\n{e}"))

        try:
            # Execute download phase
            self.root.after(0, self._set_status, "Iniciando downloads...")
            baixar_videos_para_audio(
                video_urls=urls,
                pasta_destino=pasta_destino,
                progress_callback=download_progress_hook,
                finished_callback=on_download_finished_successfully, # This callback will transition to transcription
                error_callback=lambda e: on_process_error(e, "Download")
            )
        except Exception as e:
            on_process_error(e)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()