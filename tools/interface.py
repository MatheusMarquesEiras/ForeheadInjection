import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import shutil
from videos_transcriber import Transcriber
from checker import file_exist
from download_audio import video_downloader
from processJson import JsonProcessor

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Baixar áudio do YouTube (MP3) e Transcrever")
        self.root.geometry("800x650")
        self.root.minsize(700, 600)

        self.destino = str(Path('./audios').absolute())
        self.trancriber = Transcriber()
        self._cancel_flag = False

        self.selected_image_full_path = ""
        self.image_url = ""

        # ✅ CORREÇÃO: Inicializar json_handler ANTES de _build_ui()
        self.json_handler = JsonProcessor(Path('./transcription/transcription.json'))

        self._build_ui()
        self._set_idle_state()
        self._check_form_validity()

        # ✅ Monitorar o arquivo JSON
        self._monitor_json_file()

    # ----------- Construção da UI -----------
    def _build_ui(self):
        titulo = tk.Label(self.root, text="Baixar áudio do YouTube (MP3) e Transcrever", font=("Arial", 20, "bold"))
        titulo.pack(pady=15)

        # ✅ Frame para entrada do curso
        frame_course = tk.Frame(self.root)
        frame_course.pack(fill="x", padx=20, pady=(0, 10))

        lbl_course = tk.Label(frame_course, text="Curso:", font=("Arial", 12, "bold"))
        lbl_course.pack(anchor="w")

        self.txt_course = tk.Entry(frame_course, font=("Consolas", 11))
        self.txt_course.pack(fill="x", pady=5)
        self.txt_course.bind("<KeyRelease>", lambda event: self._check_form_validity())

        # ✅ Frame para seleção de imagem (novo)
        frame_image = tk.Frame(self.root)
        frame_image.pack(fill="x", padx=20, pady=(0, 10))

        lbl_image = tk.Label(frame_image, text="Imagem do Curso:", font=("Arial", 12, "bold"))
        lbl_image.pack(anchor="w")

        frame_image_input = tk.Frame(frame_image)
        frame_image_input.pack(fill="x", pady=5)

        self.txt_image_path = tk.Entry(frame_image_input, font=("Consolas", 11), state="readonly", 
                                        readonlybackground="lightyellow", fg="black")
        self.txt_image_path.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_select_image = tk.Button(frame_image_input, text="Selecionar Imagem", command=self._select_image, font=("Arial", 10))
        self.btn_select_image.pack(side="right")

        # Frame para URLs
        frame_url = tk.Frame(self.root)
        frame_url.pack(fill="x", padx=20, pady=(0, 10))

        lbl_url = tk.Label(frame_url, text="URLs (uma por linha):", font=("Arial", 12, "bold"))
        lbl_url.pack(anchor="w")

        self.txt_urls = tk.Text(frame_url, height=4, font=("Consolas", 11))
        self.txt_urls.pack(fill="both", expand=True, pady=5)
        self.txt_urls.bind("<KeyRelease>", lambda event: self._check_form_validity())

        # Frame de progresso
        frame_prog = tk.Frame(self.root)
        frame_prog.pack(fill="x", padx=20, pady=(10, 0))

        lbl_download_bar = tk.Label(frame_prog, text="Progresso do Download:", font=("Arial", 10))
        lbl_download_bar.pack(anchor="w")
        self.download_bar = ttk.Progressbar(frame_prog, orient="horizontal", length=400, mode="determinate", maximum=100)
        self.download_bar.pack(fill="x")

        lbl_transcriber_bar = tk.Label(frame_prog, text="Progresso da Transcrição:", font=("Arial", 10))
        lbl_transcriber_bar.pack(anchor="w", pady=(8, 0))
        self.transcriber_bar = ttk.Progressbar(frame_prog, orient="horizontal", length=400, mode="determinate", maximum=100)
        self.transcriber_bar.pack(fill="x", pady=(0, 8))

        self.lbl_status = tk.Label(self.root, text="Aguardando...", font=("Arial", 12))
        self.lbl_status.pack(pady=8)

        # Frame de ações
        frame_acoes = tk.Frame(self.root)
        frame_acoes.pack(pady=10)

        self.btn_baixar = tk.Button(frame_acoes, text="Iniciar", command=self._iniciar_processo, font=("Arial", 12), width=12)
        self.btn_baixar.grid(row=0, column=0, padx=5)

        self.btn_cancelar = tk.Button(frame_acoes, text="Cancelar", command=self._cancelar, font=("Arial", 12), width=12, state="disabled")
        self.btn_cancelar.grid(row=0, column=1, padx=5)

        # ✅ CORREÇÃO: Inicializa desabilitado, será ativado quando o arquivo existir
        self.bnt_process_transcipt = tk.Button(frame_acoes, text="Processar transcrição", command=self.json_handler.process, font=("Arial", 12), width=24, state="disabled")
        self.bnt_process_transcipt.grid(row=1, column=0, columnspan=2, padx=5, pady=10)

    # ----------- Monitoramento do arquivo JSON -----------
    # ✅ NOVA FUNÇÃO: Verifica periodicamente se o arquivo JSON foi criado
    def _monitor_json_file(self):
        json_path = Path('./transcription/transcription.json')
        if file_exist(json_path) == 'active':
            self.bnt_process_transcipt.config(state="normal")
        else:
            self.bnt_process_transcipt.config(state="disabled")
        
        # Verificar novamente a cada 1 segundo (1000 ms)
        self.root.after(1000, self._monitor_json_file)

    # ----------- Estado de UI -----------
    def _set_busy_state(self):
        self.btn_baixar.config(state="disabled")
        self.btn_cancelar.config(state="normal")
        self.txt_urls.config(state="disabled")
        self.txt_course.config(state="disabled")
        self.btn_select_image.config(state="disabled")

    def _set_idle_state(self):
        self.btn_baixar.config(state="normal")
        self.btn_cancelar.config(state="disabled")
        self.txt_urls.config(state="normal")
        self.txt_course.config(state="normal")
        self.btn_select_image.config(state="normal")
        self._set_progress(0, "download")
        self._set_progress(0, "transcriber")
        self._set_status("Aguardando...")
        self._cancel_flag = False
        self._check_form_validity()

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
    
    def _check_form_validity(self):
        course_name_filled = bool(self.txt_course.get().strip())
        urls_filled = bool(self.txt_urls.get("1.0", "end").strip())
        image_selected = bool(self.selected_image_full_path)

        if course_name_filled and urls_filled and image_selected:
            self.btn_baixar.config(state="normal")
        else:
            self.btn_baixar.config(state="disabled")

    def _transcriber_progress_callback(self, current, total, percentage, filename):
        if self._cancel_flag:
            return
        p = max(0.0, min(100.0, float(percentage)))
        self.root.after(0, self._set_progress, p, "transcriber")
        self.root.after(0, self._set_status, f"Transcrevendo... {current} de {total} ({p:.1f}%) - {filename}")

    # ----------- Botões -----------
    def _select_image(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar Imagem do Curso",
            filetypes=[
                ("Arquivos de Imagem", "*.png *.jpg *.jpeg *.gif *.webp"),
                ("Todos os Arquivos", "*.*")
            ]
        )
        if file_path:
            try:
                static_dir = Path('./backend/static')
                static_dir.mkdir(parents=True, exist_ok=True)

                image_filename = Path(file_path).name
                destination_path = static_dir / image_filename

                shutil.copy(file_path, destination_path)
                
                self.txt_image_path.config(state="normal")
                self.txt_image_path.delete(0, tk.END)
                self.txt_image_path.insert(0, image_filename)
                self.txt_image_path.config(state="readonly")
                
                self.selected_image_full_path = file_path
                self.image_url = f"http://localhost:5000/static/{image_filename}"
                
                self._set_status(f"Imagem selecionada: {image_filename}")
            except Exception as e:
                messagebox.showerror("Erro de Imagem", f"Não foi possível copiar a imagem: {e}")
                self.txt_image_path.config(state="normal")
                self.txt_image_path.delete(0, tk.END)
                self.txt_image_path.config(state="readonly")
                self.selected_image_full_path = ""
                self.image_url = ""
        else:
            self.txt_image_path.config(state="normal")
            self.txt_image_path.delete(0, tk.END)
            self.txt_image_path.config(state="readonly")
            self.selected_image_full_path = ""
            self.image_url = ""
            self._set_status("Seleção de imagem cancelada.")
        
        self._check_form_validity()

    def _iniciar_processo(self):
        course_name = self.txt_course.get().strip()
        if not course_name:
            messagebox.showwarning("Atenção", "Informe o nome do curso.")
            return

        if not self.image_url:
            messagebox.showwarning("Atenção", "Selecione uma imagem do curso antes de iniciar o processo.")
            return

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

        th = threading.Thread(target=self._worker_process, args=(urls, self.destino, course_name, self.image_url), daemon=True)
        th.start()

    def _cancelar(self):
        self._cancel_flag = True
        self.root.after(0, self._set_status, "Cancelando processo...")
        self.btn_cancelar.config(state="disabled")

    # ----------- Worker em thread separada -----------
    def _worker_process(self, urls, pasta_destino, course_name, image_url):
        def download_progress_hook(d):
            if self._cancel_flag:
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

        def on_process_error(error_msg, phase="Geral"):
            self.root.after(0, self._stop_indeterminate)
            self.root.after(0, self._set_status, f"Erro durante o processo ({phase}).")
            self.root.after(0, self._set_idle_state)
            self.root.after(0, lambda: self.download_bar.config(value=0))
            self.root.after(0, lambda: self.transcriber_bar.config(value=0))
            self.root.after(0, lambda msg=error_msg, ph=phase: messagebox.showerror(
                "Erro",
                f"Ocorreu um erro na fase de {ph}:\n{msg}"
            ))

        def on_download_finished_successfully():
            if self._cancel_flag:
                self.root.after(0, self._set_status, "Processo cancelado após downloads.")
                self.root.after(0, self._set_idle_state)
                return

            self.root.after(0, self._set_status, "Download concluído! Iniciando transcrição...")
            self.root.after(0, lambda: self.transcriber_bar.config(value=0))

            try:
                self.trancriber.transribe(
                    progress_callback=self._transcriber_progress_callback,
                    cancel_check_callback=lambda: self._cancel_flag,
                    course_name=course_name,
                    image_url=image_url
                )
                self.root.after(0, self._set_status, "Transcrições concluídas!")
                self.root.after(0, self._set_progress, 100, "transcriber")
                self.root.after(0, self._set_idle_state)
            except Exception as e:
                self.root.after(0, self._set_status, "Erro durante a transcrição.")
                self.root.after(0, self._set_progress, 0, "transcriber")
                self.root.after(0, self._set_idle_state)
                self.root.after(0, lambda err=str(e): messagebox.showerror(
                    "Erro na Transcrição",
                    f"Ocorreu um erro durante a transcrição:\n{err}"
                ))

        try:
            self.root.after(0, self._set_status, "Iniciando downloads...")
            video_downloader(
                video_urls=urls,
                pasta_destino=pasta_destino,
                progress_callback=download_progress_hook,
                finished_callback=on_download_finished_successfully,
                error_callback=lambda e: on_process_error(str(e), "Download")
            )
        except Exception as e:
            on_process_error(str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()