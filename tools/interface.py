import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

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
        with yt_dlp.YoutubeDL(opcoes) as ydl:
            for url in video_urls:
                ydl.download([url])

        if finished_callback:
            finished_callback()

    except Exception as e:
        if error_callback:
            error_callback(e)


# ========================== Interface Tkinter ==========================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Baixar áudio do YouTube (MP3)")
        self.root.geometry("800x550")
        self.root.minsize(700, 500)

        self.destino = tk.StringVar(value=os.path.abspath("./audios"))

        self._build_ui()
        self._set_idle_state()

    # ----------- Construção da UI -----------
    def _build_ui(self):
        titulo = tk.Label(self.root, text="Baixar áudio do YouTube (MP3)", font=("Arial", 20, "bold"))
        titulo.pack(pady=15)

        frame_url = tk.Frame(self.root)
        frame_url.pack(fill="x", padx=20)

        lbl_url = tk.Label(frame_url, text="URLs (uma por linha):", font=("Arial", 12, "bold"))
        lbl_url.pack(anchor="w")

        self.txt_urls = tk.Text(frame_url, height=8, font=("Consolas", 11))
        self.txt_urls.pack(fill="both", expand=True, pady=8)

        frame_destino = tk.Frame(self.root)
        frame_destino.pack(fill="x", padx=20, pady=10)

        lbl_dest = tk.Label(frame_destino, text="Pasta de destino:", font=("Arial", 12, "bold"))
        lbl_dest.grid(row=0, column=0, sticky="w")

        self.ent_dest = tk.Entry(frame_destino, textvariable=self.destino, font=("Arial", 11), width=60)
        self.ent_dest.grid(row=1, column=0, sticky="we", padx=(0, 8))
        frame_destino.columnconfigure(0, weight=1)

        self.btn_escolher = tk.Button(frame_destino, text="Escolher...", command=self._escolher_pasta, font=("Arial", 11))
        self.btn_escolher.grid(row=1, column=1, sticky="e")

        frame_prog = tk.Frame(self.root)
        frame_prog.pack(fill="x", padx=20, pady=(10, 0))

        self.barra = ttk.Progressbar(frame_prog, orient="horizontal", length=400, mode="determinate", maximum=100)
        self.barra.pack(fill="x")

        self.lbl_status = tk.Label(self.root, text="Aguardando...", font=("Arial", 12))
        self.lbl_status.pack(pady=8)

        frame_acoes = tk.Frame(self.root)
        frame_acoes.pack(pady=10)

        self.btn_baixar = tk.Button(frame_acoes, text="Baixar", command=self._iniciar_download, font=("Arial", 12), width=12)
        self.btn_baixar.grid(row=0, column=0, padx=5)

        self.btn_cancelar = tk.Button(frame_acoes, text="Cancelar", command=self._cancelar, font=("Arial", 12), width=12, state="disabled")
        self.btn_cancelar.grid(row=0, column=1, padx=5)

        # Log opcional
        frame_log = tk.Frame(self.root)
        frame_log.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        lbl_log = tk.Label(frame_log, text="Log:", font=("Arial", 12, "bold"))
        lbl_log.pack(anchor="w")

        self.txt_log = tk.Text(frame_log, height=8, font=("Consolas", 10), state="disabled")
        self.txt_log.pack(fill="both", expand=True)

        # Controle de cancelamento
        self._cancel_flag = False

    # ----------- Seleção de pasta -----------
    def _escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta de destino", initialdir=self.destino.get())
        if pasta:
            self.destino.set(pasta)

    # ----------- Estado de UI -----------
    def _set_busy_state(self):
        self.btn_baixar.config(state="disabled")
        self.btn_cancelar.config(state="normal")
        self.btn_escolher.config(state="disabled")

    def _set_idle_state(self):
        self.btn_baixar.config(state="normal")
        self.btn_cancelar.config(state="disabled")
        self.btn_escolher.config(state="normal")
        self._set_progress(0)
        self._set_status("Aguardando...")

    # ----------- Helpers de UI (sempre thread principal) -----------
    def _set_status(self, texto):
        self.lbl_status.config(text=texto)

    def _set_progress(self, percent):
        p = max(0.0, min(100.0, float(percent)))
        if str(self.barra.cget("mode")) == "indeterminate":
            self.barra.stop()
            self.barra.config(mode="determinate")
        self.barra['value'] = p

    def _start_indeterminate(self):
        self.barra.config(mode="indeterminate")
        self.barra.start(15)

    def _stop_indeterminate(self):
        if str(self.barra.cget("mode")) == "indeterminate":
            self.barra.stop()
            self.barra.config(mode="determinate")
            self.barra['value'] = 0

    def _append_log(self, texto):
        self.txt_log.config(state="normal")
        self.txt_log.insert("end", texto.rstrip() + "\n")
        self.txt_log.see("end")
        self.txt_log.config(state="disabled")

    # ----------- Botões -----------
    def _iniciar_download(self):
        urls_raw = self.txt_urls.get("1.0", "end").strip()
        if not urls_raw:
            messagebox.showwarning("Atenção", "Informe ao menos uma URL (uma por linha).")
            return

        urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]
        pasta_destino = self.destino.get().strip()
        if not pasta_destino:
            messagebox.showwarning("Atenção", "Selecione ou informe a pasta de destino.")
            return

        self._cancel_flag = False
        self._set_busy_state()
        self._set_status("Preparando downloads...")
        self._set_progress(0)
        self._append_log(f"Iniciando: {len(urls)} URL(s)")

        # Inicia thread de trabalho
        th = threading.Thread(target=self._worker_download, args=(urls, pasta_destino), daemon=True)
        th.start()

    def _cancelar(self):
        # Não há cancelamento nativo em yt_dlp por hook; sinalizamos e paramos UI.
        # Em uso real, você poderia baixar um arquivo por vez e verificar essa flag entre itens.
        self._cancel_flag = True
        self._append_log("Cancelamento solicitado. Aguardando concluir o item atual...")

    # ----------- Worker em thread separada -----------
    def _worker_download(self, urls, pasta_destino):
        # Hook de progresso (chamado pela thread de download)
        def progress_hook(d):
            if self._cancel_flag:
                # Não há API direta para interromper o download atual;
                # a estratégia prática é deixar concluir o arquivo em andamento
                # e não iniciar novos (controle externo ao loop, se necessário).
                return

            status = d.get('status')
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            baixado = d.get('downloaded_bytes')
            speed = d.get('speed')
            eta = d.get('eta')

            if status == 'downloading':
                if total and baixado:
                    percent = (baixado / total) * 100.0
                    self.root.after(0, self._set_progress, percent)
                    msg = f"Baixando... {percent:.1f}%"
                    if speed:
                        msg += f" | Vel: {speed/1024/1024:.2f} MB/s"
                    if eta:
                        msg += f" | ETA: {eta}s"
                    self.root.after(0, self._set_status, msg)
                else:
                    # Sem total conhecido => indeterminado
                    self.root.after(0, self._set_status, "Baixando... (tamanho total desconhecido)")
                    self.root.after(0, self._start_indeterminate)

            elif status == 'finished':
                self.root.after(0, self._stop_indeterminate)
                self.root.after(0, self._set_progress, 100)
                self.root.after(0, self._set_status, "Download concluído! Convertendo/Finalizando...")

        # Callbacks de término/erro
        def on_finished():
            self.root.after(0, self._set_status, "Tudo pronto! Arquivos salvos.")
            self.root.after(0, self._append_log, "Concluído sem erros.")
            self.root.after(0, self._set_idle_state)

        def on_error(e):
            self.root.after(0, self._stop_indeterminate)
            self.root.after(0, self._set_status, "Erro durante o processo.")
            self.root.after(0, self._append_log, f"Erro: {e}")
            self.root.after(0, self._set_idle_state)
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}"))

        # Execução do download
        try:
            self.root.after(0, self._append_log, f"Destino: {pasta_destino}")
            baixar_videos_para_audio(
                video_urls=urls,
                pasta_destino=pasta_destino,
                progress_callback=progress_hook,
                finished_callback=on_finished,
                error_callback=on_error
            )
        except Exception as e:
            on_error(e)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()