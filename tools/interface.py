import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
import shutil
import os
import json
import re  # Importação de Regex
import pandas as pd

# Importações do projeto
from videos_transcriber import Transcriber
from checker import file_exist
from download_audio import video_downloader
from processJson import JsonProcessor
from ai_core import OllamaServer

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento & IA")
        self.root.geometry("950x800") 
        self.root.minsize(800, 600)

        # --- Configurações Iniciais ---
        self.destino = str(Path('./audios').absolute())
        self.trancriber = Transcriber()
        self._cancel_flag = False
        self.selected_image_full_path = ""
        self.image_url = ""
        self.db_path = Path('./backend/data.json')
        
        # Variável para armazenar o tópico atual da atividade sendo gerada
        self.current_activity_topic = None 

        # Inicializar processadores
        self.json_handler = JsonProcessor(Path('./transcription/transcription.json'), self.db_path)
        
        # Inicializar Servidor Ollama
        self.ollama_server = OllamaServer()
        
        # PULL automático ao iniciar (background)
        threading.Thread(target=self._worker_pull_silent, daemon=True).start()

        # --- Configuração das Abas (Notebook) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab_downloader = tk.Frame(self.notebook)
        self.tab_generator = tk.Frame(self.notebook)

        self.notebook.add(self.tab_downloader, text='Downloader')
        self.notebook.add(self.tab_generator, text='Gerador de Atividade')

        # --- Construção da UI ---
        self._build_downloader_ui()
        self._build_generator_ui()

        # Estados e Monitores
        self._set_idle_state()
        self._check_form_validity()
        self._monitor_json_file()

    # =========================================================================
    #                           ABA 1: DOWNLOADER UI
    # =========================================================================
    def _build_downloader_ui(self):
        container = tk.Frame(self.tab_downloader)
        container.pack(fill="both", expand=True)

        titulo = tk.Label(container, text="Sistema Gerenciamento Interno", font=("Arial", 18, "bold"))
        titulo.pack(pady=10)

        # --- Curso ---
        frame_course = tk.Frame(container)
        frame_course.pack(fill="x", padx=20)
        tk.Label(frame_course, text="Curso:", font=("Arial", 11, "bold")).pack(anchor="w")
        self.txt_course = tk.Entry(frame_course, font=("Consolas", 11))
        self.txt_course.pack(fill="x", pady=2)
        self.txt_course.bind("<KeyRelease>", lambda event: self._check_form_validity())

        # --- Imagem ---
        frame_image = tk.Frame(container)
        frame_image.pack(fill="x", padx=20, pady=5)
        tk.Label(frame_image, text="Imagem do Curso:", font=("Arial", 11, "bold")).pack(anchor="w")
        
        f_img_input = tk.Frame(frame_image)
        f_img_input.pack(fill="x")
        self.txt_image_path = tk.Entry(f_img_input, font=("Consolas", 10), state="readonly", readonlybackground="#f0f0f0")
        self.txt_image_path.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_select_image = tk.Button(f_img_input, text="Selecionar", command=self._select_image)
        self.btn_select_image.pack(side="right")

        # --- URLs ---
        frame_url = tk.Frame(container)
        frame_url.pack(fill="x", padx=20, pady=5)
        tk.Label(frame_url, text="URLs (uma por linha):", font=("Arial", 11, "bold")).pack(anchor="w")
        self.txt_urls = tk.Text(frame_url, height=4, font=("Consolas", 10))
        self.txt_urls.pack(fill="x", pady=2)
        self.txt_urls.bind("<KeyRelease>", lambda event: self._check_form_validity())

        # --- Progresso ---
        frame_prog = tk.Frame(container)
        frame_prog.pack(fill="x", padx=20, pady=10)
        
        tk.Label(frame_prog, text="Download:").pack(anchor="w")
        self.download_bar = ttk.Progressbar(frame_prog, orient="horizontal", length=100, mode="determinate")
        self.download_bar.pack(fill="x")
        
        tk.Label(frame_prog, text="Transcrição:").pack(anchor="w", pady=(5,0))
        self.transcriber_bar = ttk.Progressbar(frame_prog, orient="horizontal", length=100, mode="determinate")
        self.transcriber_bar.pack(fill="x")

        self.lbl_status = tk.Label(container, text="Aguardando...", font=("Arial", 10))
        self.lbl_status.pack(pady=5)

        # --- Botões ---
        frame_btns = tk.Frame(container)
        frame_btns.pack(pady=10)
        self.btn_baixar = tk.Button(frame_btns, text="Iniciar", command=self._iniciar_processo, width=15, bg="#dddddd")
        self.btn_baixar.grid(row=0, column=0, padx=5)
        self.btn_cancelar = tk.Button(frame_btns, text="Cancelar", command=self._cancelar, width=15, state="disabled")
        self.btn_cancelar.grid(row=0, column=1, padx=5)

        self.bnt_process_transcipt = tk.Button(frame_btns, text="Processar JSON", command=self._executar_processamento_json, width=32, state="disabled")
        self.bnt_process_transcipt.grid(row=1, column=0, columnspan=2, pady=5)
        
        self.bnt_put_in_db = tk.Button(frame_btns, text="Salvar no DB e Limpar", command=self._adicionar_ao_db_e_limpar, width=32, state="disabled", bg="#cceeff")
        self.bnt_put_in_db.grid(row=2, column=0, columnspan=2, pady=5)

    # =========================================================================
    #                           ABA 2: GERADOR DE ATIVIDADE (IA)
    # =========================================================================
    def _build_generator_ui(self):
        container = tk.Frame(self.tab_generator)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        tk.Label(container, text="Gerador de Atividades com IA", font=("Arial", 16, "bold")).pack(pady=(0, 15))

        # -- Área Superior: Lista de Tópicos --
        frame_top = tk.Frame(container)
        frame_top.pack(fill="both", expand=True, pady=(0, 10))

        # Lado Esquerdo: Lista
        frame_list = tk.Frame(frame_top)
        frame_list.pack(side="left", fill="both", expand=True)

        tk.Label(frame_list, text="Selecione um Tópico (Vídeo):", font=("Arial", 10, "bold")).pack(anchor="w")
        
        scrollbar_list = tk.Scrollbar(frame_list)
        scrollbar_list.pack(side="right", fill="y")
        
        self.listbox_videos = tk.Listbox(frame_list, font=("Arial", 10), selectmode="single", yscrollcommand=scrollbar_list.set)
        self.listbox_videos.pack(side="left", fill="both", expand=True)
        scrollbar_list.config(command=self.listbox_videos.yview)
        
        self.listbox_videos.bind("<<ListboxSelect>>", self._on_video_select)

        # Lado Direito: Botões de Ação da Aba 2
        frame_actions = tk.Frame(frame_top)
        frame_actions.pack(side="right", fill="y", padx=(10, 0))
        
        self.btn_refresh_list = tk.Button(frame_actions, text="🔄 Atualizar Lista", command=self._carregar_lista_videos_pandas)
        self.btn_refresh_list.pack(fill="x", pady=2)

        self.btn_pull_model = tk.Button(frame_actions, text="📥 Baixar Modelo", command=self._pull_model_manual)
        self.btn_pull_model.pack(fill="x", pady=2)

        self.btn_generate_activity = tk.Button(frame_actions, text="✨ Gerar Atividade", command=self._gerar_atividade_ia, state="disabled", bg="#d9ffcc")
        self.btn_generate_activity.pack(fill="x", pady=(20, 2))

        # -- Área Central: Saída da IA --
        frame_bottom = tk.Frame(container)
        frame_bottom.pack(fill="both", expand=True, pady=(0, 10))

        tk.Label(frame_bottom, text="Resposta da IA:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.txt_ai_output = scrolledtext.ScrolledText(frame_bottom, font=("Consolas", 10), state="disabled", height=15)
        self.txt_ai_output.pack(fill="both", expand=True)

        # -- Área Inferior: Botões de Decisão (Aceitar/Negar) --
        frame_decision = tk.Frame(container)
        frame_decision.pack(fill="x")

        # Botão Negar (Vermelho Claro)
        self.btn_deny = tk.Button(frame_decision, text="❌ Negar (Gerar Outra)", command=self._negar_atividade, 
                                  font=("Arial", 11, "bold"), bg="#ffcccc", state="disabled", height=2)
        self.btn_deny.pack(side="left", expand=True, fill="x", padx=(0, 5))

        # Botão Aceitar (Verde Claro)
        self.btn_accept = tk.Button(frame_decision, text="✅ Aceitar", command=self._aceitar_atividade, 
                                    font=("Arial", 11, "bold"), bg="#ccffcc", state="disabled", height=2)
        self.btn_accept.pack(side="right", expand=True, fill="x", padx=(5, 0))

    # =========================================================================
    #                  LÓGICA DA ABA 2 (PANDAS + OLLAMA)
    # =========================================================================

    def _pull_model_manual(self):
        self.btn_pull_model.config(state="disabled", text="Baixando...")
        threading.Thread(target=self._worker_pull_manual, daemon=True).start()

    def _worker_pull_manual(self):
        try:
            print(">>> Iniciando download do modelo via Interface...")
            self.ollama_server.pull()
            print(">>> TERMINOU DE BAIXAR O MODELO.")
            messagebox.showinfo("Ollama", "Modelo atualizado com sucesso!")
        except Exception as e:
            print(f"Erro no pull: {e}")
            messagebox.showerror("Erro", f"Falha ao baixar modelo: {e}")
        finally:
            self.root.after(0, lambda: self.btn_pull_model.config(state="normal", text="📥 Baixar Modelo"))

    def _worker_pull_silent(self):
        try:
            self.ollama_server.pull()
            print(">>> (Background) Modelo verificado/atualizado.")
        except: pass

    def _carregar_lista_videos_pandas(self):
        if not self.db_path.exists():
            messagebox.showwarning("Aviso", "Banco de dados vazio.")
            return

        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'contents' not in data or not data['contents']:
                self.listbox_videos.delete(0, tk.END)
                self.listbox_videos.insert(tk.END, "Sem dados.")
                return

            df = pd.DataFrame(data['contents'])

            if 'type_content' in df.columns and 'topic_reference' in df.columns:
                topics = df[df['type_content'] == 'video']['topic_reference'].unique()
                self.listbox_videos.delete(0, tk.END)
                for topic in topics:
                    self.listbox_videos.insert(tk.END, topic)
            else:
                messagebox.showerror("Erro", "Estrutura do JSON inválida.")

        except Exception as e:
            messagebox.showerror("Erro Pandas", f"Erro ao ler dados: {e}")

    def _on_video_select(self, event):
        if self.listbox_videos.curselection():
            self.btn_generate_activity.config(state="normal")
        else:
            self.btn_generate_activity.config(state="disabled")

    # --- Geração de Atividade ---
    def _gerar_atividade_ia(self):
        selection = self.listbox_videos.curselection()
        if not selection:
            return
        
        # Captura o tópico e armazena na variável da classe
        topic_selected = self.listbox_videos.get(selection[0])
        self.current_activity_topic = topic_selected

        self.btn_generate_activity.config(state="disabled", text="Gerando...")
        self.btn_deny.config(state="disabled")
        self.btn_accept.config(state="disabled")
        
        self.txt_ai_output.config(state="normal")
        self.txt_ai_output.delete("1.0", tk.END)
        self.txt_ai_output.insert(tk.END, "⏳ Processando dados e consultando IA (pode demorar)...\n")
        self.txt_ai_output.config(state="disabled")

        threading.Thread(target=self._worker_ia, args=(topic_selected,), daemon=True).start()

    def _worker_ia(self, topic_selected):
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data['contents'])

            mask = (df['topic_reference'] == topic_selected) & (df['type_content'] == 'transcription')
            transcription_df = df[mask].sort_values(by='sequence')

            if transcription_df.empty:
                self._update_ai_output(f"Erro: Nenhuma transcrição encontrada para o tópico '{topic_selected}'.")
                return

            full_text = " ".join(transcription_df['content'].astype(str).tolist())
            prompt_user = f"Conteúdo da aula para gerar atividade:\n\n{full_text}"
            
            response_content = self.ollama_server.get_answer(prompt_user)
            self._update_ai_output(response_content)
            
            # Habilita botões de decisão
            self.root.after(0, lambda: self.btn_deny.config(state="normal"))
            self.root.after(0, lambda: self.btn_accept.config(state="normal"))

        except Exception as e:
            self._update_ai_output(f"Erro durante o processamento: {e}")
        
        finally:
            self.root.after(0, lambda: self.btn_generate_activity.config(state="normal", text="✨ Gerar Atividade"))

    def _update_ai_output(self, text):
        def _update():
            self.txt_ai_output.config(state="normal")
            self.txt_ai_output.delete("1.0", tk.END)
            self.txt_ai_output.insert(tk.END, text)
            self.txt_ai_output.config(state="disabled")
        self.root.after(0, _update)

    # ✅ Função: NEGAR
    def _negar_atividade(self):
        """Nega a atividade atual e manda gerar outra imediatamente"""
        self._gerar_atividade_ia()

    # ✅ Função de Parsing (Transforma Texto -> Objeto JSON Estruturado)
    def _parse_ai_response_to_json(self, text):
        """
        Lê a string retornada pela IA e converte em uma lista de dicionários
        no formato especificado: {question, opitions: {a,b,c,d}, correcti_answer}
        """
        questions_list = []
        
        # Regex flexíveis para capturar os padrões (lidando com possíveis problemas de encoding)
        # Captura: **Questão X:** Enunciado
        question_pattern = r"\*\*Quest(?:ã|Ã£|a)o\s*\d+:\*\*\s*(.+)"
        
        # Captura: a) Texto, b) Texto...
        option_pattern = r"^\s*([a-dA-D])\)\s*(.+)"
        
        # Captura: **Resposta Correta:** a
        answer_pattern = r"\*\*Resposta Correta:\*\*\s*([a-dA-D])"

        lines = text.split('\n')
        
        current_question = None
        
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # Verifica se é uma nova questão
            q_match = re.search(question_pattern, line, re.IGNORECASE)
            if q_match:
                # Se já tinha uma questão sendo montada, salva ela
                if current_question:
                    questions_list.append(current_question)
                
                # Inicia nova questão
                current_question = {
                    "question": q_match.group(1).strip(),
                    "opitions": {}, # Mantendo o typo solicitado 'opitions'
                    "correcti_answer": "" # Mantendo o typo solicitado 'correcti_answer'
                }
                continue
            
            # Verifica se é uma opção (a, b, c, d)
            opt_match = re.search(option_pattern, line)
            if opt_match and current_question:
                letter = opt_match.group(1).lower()
                content = opt_match.group(2).strip()
                current_question["opitions"][letter] = content
                continue

            # Verifica se é a resposta
            ans_match = re.search(answer_pattern, line, re.IGNORECASE)
            if ans_match and current_question:
                # Salva apenas a letra (ex: 'd')
                current_question["correcti_answer"] = ans_match.group(1).lower()
                continue
        
        # Adiciona a última questão processada
        if current_question:
            questions_list.append(current_question)
            
        return questions_list

    # ✅ Função: ACEITAR
    def _aceitar_atividade(self):
        """Aceita a atividade, parseia, formata e salva no data.json"""
        
        # 1. Pegar o texto da tela
        raw_text = self.txt_ai_output.get("1.0", tk.END).strip()
        if not raw_text or "Erro" in raw_text or "Processando" in raw_text:
            messagebox.showwarning("Aviso", "Não há atividade válida para salvar.")
            return

        try:
            # 2. Parsear o texto para a estrutura de objetos
            questions_parsed = self._parse_ai_response_to_json(raw_text)
            
            if not questions_parsed:
                messagebox.showerror("Erro", "Não foi possível converter o texto da IA para o formato JSON. Verifique se o formato está correto.")
                return

            # 3. Ler o data.json atual
            with open(self.db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)

            # 4. Encontrar a última sequência do tópico atual
            if not self.current_activity_topic:
                messagebox.showerror("Erro", "Tópico de referência perdido. Selecione o vídeo novamente.")
                return
            
            # Filtra conteúdos deste tópico para achar a maior sequência
            df = pd.DataFrame(db_data['contents'])
            
            if not df.empty and 'topic_reference' in df.columns:
                topic_contents = df[df['topic_reference'] == self.current_activity_topic]
                if not topic_contents.empty:
                    last_sequence = topic_contents['sequence'].max()
                else:
                    last_sequence = 0
            else:
                last_sequence = 0
            
            new_sequence = int(last_sequence) + 1

            # 5. Criar o objeto final da atividade
            new_activity_entry = {
                "type_content": "activity",
                "content": questions_parsed, # Lista de questões
                "topic_reference": self.current_activity_topic,
                "sequence": new_sequence
            }

            # 6. Adicionar ao banco e salvar
            db_data['contents'].append(new_activity_entry)

            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, ensure_ascii=False, indent=4)

            # 7. Feedback e Limpeza
            messagebox.showinfo("Sucesso", f"Atividade salva com sucesso!\nSequência: {new_sequence}")
            
            self.txt_ai_output.config(state="normal")
            self.txt_ai_output.delete("1.0", tk.END)
            self.txt_ai_output.config(state="disabled")
            
            self.btn_deny.config(state="disabled")
            self.btn_accept.config(state="disabled")
            self.btn_generate_activity.config(state="normal")

        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro ao salvar no banco:\n{e}")
            print(e)

    # =========================================================================
    #                  LÓGICA DA ABA 1 (DOWNLOADER)
    # =========================================================================
    
    def _executar_processamento_json(self):
        urls_raw = self.txt_urls.get("1.0", "end").strip()
        urls_list = []
        if urls_raw:
            urls_list = [u.strip() for u in urls_raw.splitlines() if u.strip()]
        try:
            self.json_handler.process(video_urls=urls_list)
            messagebox.showinfo("Sucesso", "Processado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _adicionar_ao_db_e_limpar(self):
        try:
            self.json_handler.put_in_db()
            messagebox.showinfo("Sucesso", "Salvo no DB!")
            
            self.txt_course.delete(0, tk.END)
            self.txt_urls.delete("1.0", tk.END)
            self.txt_image_path.config(state="normal")
            self.txt_image_path.delete(0, tk.END)
            self.txt_image_path.config(state="readonly")
            self.selected_image_full_path = ""
            self.image_url = ""

            audios_path = Path('./audios')
            if audios_path.exists():
                for item in audios_path.iterdir():
                    try:
                        if item.is_file(): item.unlink()
                        elif item.is_dir(): shutil.rmtree(item)
                    except: pass

            transc_file = Path('./transcription/transcription.json')
            if transc_file.exists():
                try: transc_file.unlink()
                except: pass

            self._set_idle_state()
            self._set_status("Limpo.")
            self._monitor_json_file()
            self._carregar_lista_videos_pandas()

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def _monitor_json_file(self):
        json_path = Path('./transcription/transcription.json')
        if file_exist(json_path):
            self.bnt_process_transcipt.config(state="normal")
            self.bnt_put_in_db.config(state="normal")
        else:
            self.bnt_process_transcipt.config(state="disabled")
            self.bnt_put_in_db.config(state="disabled")
        self.root.after(1000, self._monitor_json_file)

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
        if self.txt_course.get().strip() and self.txt_urls.get("1.0", "end").strip() and self.selected_image_full_path:
            self.btn_baixar.config(state="normal")
        else:
            self.btn_baixar.config(state="disabled")

    def _transcriber_progress_callback(self, current, total, percentage, filename):
        if self._cancel_flag: return
        p = max(0.0, min(100.0, float(percentage)))
        self.root.after(0, self._set_progress, p, "transcriber")
        self.root.after(0, self._set_status, f"Transcrevendo... {current}/{total} ({p:.1f}%)")

    def _select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.webp")])
        if file_path:
            try:
                static_dir = Path('./backend/static')
                static_dir.mkdir(parents=True, exist_ok=True)
                fname = Path(file_path).name
                shutil.copy(file_path, static_dir / fname)
                self.txt_image_path.config(state="normal")
                self.txt_image_path.delete(0, tk.END)
                self.txt_image_path.insert(0, fname)
                self.txt_image_path.config(state="readonly")
                self.selected_image_full_path = file_path
                self.image_url = f"http://localhost:5000/static/{fname}"
                self._check_form_validity()
            except Exception as e:
                messagebox.showerror("Erro", str(e))

    def _iniciar_processo(self):
        urls = [u.strip() for u in self.txt_urls.get("1.0", "end").splitlines() if u.strip()]
        self._set_busy_state()
        self._set_status("Iniciando...")
        threading.Thread(target=self._worker_process, args=(urls, self.destino, self.txt_course.get(), self.image_url), daemon=True).start()

    def _cancelar(self):
        self._cancel_flag = True
        self._set_status("Cancelando...")

    def _worker_process(self, urls, destino, course, img_url):
        try:
            self.root.after(0, self._start_indeterminate)
            video_downloader(
                video_urls=urls, pasta_destino=destino,
                progress_callback=lambda d: self.root.after(0, self._set_status, "Baixando..."),
                finished_callback=lambda: self._on_download_done(course, img_url),
                error_callback=lambda e: messagebox.showerror("Erro", e)
            )
        except Exception as e:
            self.root.after(0, self._set_idle_state)

    def _on_download_done(self, course, img_url):
        self.root.after(0, self._stop_indeterminate)
        self.root.after(0, self._set_status, "Transcrevendo...")
        try:
            self.trancriber.transribe(
                progress_callback=self._transcriber_progress_callback,
                cancel_check_callback=lambda: self._cancel_flag,
                course_name=course, image_url=img_url
            )
            self.root.after(0, self._set_idle_state)
            self.root.after(0, self._set_status, "Concluído!")
        except Exception as e:
             self.root.after(0, self._set_idle_state)
             messagebox.showerror("Erro Transcrição", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()