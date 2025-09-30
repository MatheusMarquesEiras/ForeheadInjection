import tkinter as tk
from tkinter import ttk
import threading
import yt_dlp

# Função de download
def baixar_videos_para_audio(video_urls, pasta_destino, progress_callback=None):
    opcoes = {
        'format': 'bestaudio/best',
        'outtmpl': f'{pasta_destino}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [progress_callback] if progress_callback else []
    }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        for url in video_urls:
            try:
                ydl.download([url])
            except Exception as e:
                print(f"Erro ao baixar {url}: {e}")

# Hook para atualizar a barra
def progresso(d):
    if d['status'] == 'downloading':
        try:
            porcentagem = float(d['_percent_str'].replace('%', '').strip())
            barra['value'] = porcentagem
            janela.update_idletasks()
        except:
            pass
    elif d['status'] == 'finished':
        barra['value'] = 100
        label.config(text="Download concluído!")

# Função chamada pelo botão
def iniciar_download():
    url = entrada.get()
    label.config(text="Baixando...")
    barra['value'] = 0

    # Executar em thread separada
    t = threading.Thread(target=baixar_videos_para_audio, args=([url], ".", progresso))
    t.start()

# ---------------- Tkinter ----------------
janela = tk.Tk()
janela.title("Sistema interno")
janela.geometry("800x600")
janela.minsize(500, 600)

# Título
titulo = tk.Label(janela, text="Sistema interno", font=("Arial", 20, "bold"))
titulo.pack(pady=20)

# Campo de entrada
entrada = tk.Entry(janela, font=("Arial", 14), width=50)
entrada.pack(pady=10)

# Botão
botao = tk.Button(janela, text="Baixar", command=iniciar_download, font=("Arial", 12))
botao.pack(pady=10)

# Barra de progresso
barra = ttk.Progressbar(janela, orient="horizontal", length=400, mode="determinate")
barra.pack(pady=20)

# Rótulo
label = tk.Label(janela, text="", font=("Arial", 14))
label.pack(pady=10)

janela.mainloop()
