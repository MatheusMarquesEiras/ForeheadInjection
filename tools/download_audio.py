import yt_dlp
import os

def video_downloader(video_urls, pasta_destino, progress_callback=None, finished_callback=None, error_callback=None):
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
        'extractor_args': {
            'youtube': {
                'player_client': ['android']
            }
        },
        'retries': 10,
        'fragment_retries': 10,
        'ignoreerrors': True,
        'noplaylist': True,
        'concurrent_fragment_downloads': 1,
        'progress_hooks': [progress_callback] if progress_callback else []
    }

    try:
        ydl_instance = yt_dlp.YoutubeDL(opcoes)
        for url in video_urls:
            ydl_instance.download([url])

        if finished_callback:
            finished_callback()

    except Exception as e:
        if error_callback:
            error_callback(e)

# def baixar_videos_para_audio(video_urls, pasta_destino):
#     """
#     Baixa vídeos do YouTube e converte para áudio em formato MP3.
    
#     Args:
#         video_urls (list): Lista de URLs dos vídeos do YouTube.
#         pasta_destino (str): Caminho da pasta onde os arquivos serão salvos.
#     """
#     opcoes = {
#         'format': 'bestaudio/best',
#         'outtmpl': f'{pasta_destino}/%(title)s.%(ext)s',  # Nomeia os arquivos com base no título do vídeo
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',  # Qualidade do áudio em kbps
#         }],
#     }

#     with yt_dlp.YoutubeDL(opcoes) as ydl:
#         for url in video_urls:
#             try:
#                 print(f"Baixando: {url}")
#                 ydl.download([url])
#             except Exception as e:
#                 print(f"Erro ao baixar {url}: {e}")

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
