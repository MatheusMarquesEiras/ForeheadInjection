import yt_dlp

def baixar_videos_mp4(video_urls, pasta_destino):
    """
    Baixa vídeos do YouTube em formato MP4.
    """
    opcoes = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
        'outtmpl': f'{pasta_destino}/%(title)s.%(ext)s',  # Nome do arquivo baseado no título
        'merge_output_format': 'mp4',  # Garante que o resultado final seja MP4
    }

    with yt_dlp.YoutubeDL(opcoes) as ydl:
        for url in video_urls:
            try:
                print(f"Baixando vídeo: {url}")
                ydl.download([url])
            except Exception as e:
                print(f"Erro ao baixar {url}: {e}")

# Exemplo de uso
if __name__ == "__main__":
    videos = [
        "https://www.youtube.com/watch?v=JiOc0r31-Os&t=1327s"
    ]
    pasta_destino = "./videos"
    baixar_videos_mp4(videos, pasta_destino)
