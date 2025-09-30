import yt_dlp

def baixar_videos_para_audio(video_urls, pasta_destino):
    """
    Baixa vídeos do YouTube e converte para áudio em formato MP3.
    
    Args:
        video_urls (list): Lista de URLs dos vídeos do YouTube.
        pasta_destino (str): Caminho da pasta onde os arquivos serão salvos.
    """
    opcoes = {
        'format': 'bestaudio/best',
        'outtmpl': f'{pasta_destino}/%(title)s.%(ext)s',  # Nomeia os arquivos com base no título do vídeo
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',  # Qualidade do áudio em kbps
        }],
    }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        for url in video_urls:
            try:
                print(f"Baixando: {url}")
                ydl.download([url])
            except Exception as e:
                print(f"Erro ao baixar {url}: {e}")

# Exemplo de uso
if __name__ == "__main__":
    # Lista de URLs dos vídeos que você quer baixar
    videos = [
        "https://www.youtube.com/watch?v=ivwNWE9BgEg"
    ]

    # Caminho onde os arquivos serão salvos
    pasta_destino = "./audios"

    # Baixa os vídeos e converte para MP3
    baixar_videos_para_audio(videos, pasta_destino)
