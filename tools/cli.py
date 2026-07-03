#!/usr/bin/env python3
"""
CLI para adicionar cursos ao data.json automaticamente.

Uso básico:
  python tools/cli.py --course "Python" --image python.png URL1 URL2 ...

Exemplos:
  # Modelo turbo do faster-whisper com rate limit anti-bot (recomendado)
  python tools/cli.py --course "Pygame" --image pygame.jpg --model large-v3-turbo --rate-limit \\
      https://youtu.be/abc123 https://youtu.be/def456

  # Imagem local (copiada automaticamente para backend/static/)
  python tools/cli.py --course "React" --image /home/user/react.png \\
      https://youtu.be/xyz789

  # Usar whisper original (mais lento)
  python tools/cli.py --course "Java" --image java.png --backend whisper --model turbo \\
      https://youtu.be/aaa111

  # Manter arquivos temporários após processar
  python tools/cli.py --course "C" --image clang.png --keep \\
      https://youtu.be/bbb222

Modelos faster-whisper: tiny, base, small, medium, large-v2, large-v3, large-v3-turbo
Modelos whisper:        tiny, base, small, medium, large, turbo
"""

import argparse
import json
import os
import random
import shutil
import sys
import time
from pathlib import Path

# Força UTF-8 no stdout/stderr para não quebrar com nomes de arquivo especiais
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

TOOLS_DIR = Path(__file__).parent.resolve()
ROOT      = TOOLS_DIR.parent.resolve()

AUDIOS_DIR         = ROOT / 'audios'
TRANSCRIPTION_DIR  = ROOT / 'transcription'
TRANSCRIPTION_FILE = TRANSCRIPTION_DIR / 'transcription.json'
DB_FILE            = ROOT / 'backend' / 'data.json'
STATIC_DIR         = ROOT / 'backend' / 'static'

sys.path.insert(0, str(TOOLS_DIR))

from processJson import JsonProcessor


# ---------------------------------------------------------------------------
# Helpers de log
# ---------------------------------------------------------------------------

def _step(msg):   print(f'\n[>>] {msg}')
def _done(msg):   print(f'[OK] {msg}')
def _info(msg):   print(f'     {msg}')
def _warn(msg):   print(f'[!]  {msg}', file=sys.stderr)
def _err(msg):    print(f'[ERR] {msg}', file=sys.stderr)


# ---------------------------------------------------------------------------
# Imagem
# ---------------------------------------------------------------------------

def resolve_image(image_arg: str) -> str:
    if image_arg.startswith('http://') or image_arg.startswith('https://'):
        return image_arg

    candidate = Path(image_arg)
    if candidate.exists():
        STATIC_DIR.mkdir(parents=True, exist_ok=True)
        dest = STATIC_DIR / candidate.name
        if candidate.resolve() != dest.resolve():
            shutil.copy(candidate, dest)
            _done(f'Imagem copiada → {dest.name}')
        return f'http://localhost:5000/static/{candidate.name}'

    # Nome simples — assume que já está em backend/static/
    return f'http://localhost:5000/static/{image_arg}'


# ---------------------------------------------------------------------------
# Download com rate limiting anti-bot
# ---------------------------------------------------------------------------

def download_audios(urls: list[str], rate_limit: bool):
    """Baixa cada URL como MP3; com rate_limit dorme entre requests."""
    import yt_dlp

    AUDIOS_DIR.mkdir(parents=True, exist_ok=True)

    options = {
        'format': 'bestaudio/best',
        'outtmpl': str(AUDIOS_DIR / '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
        'retries': 10,
        'fragment_retries': 10,
        'ignoreerrors': True,
        'noplaylist': True,
        'quiet': False,
        # Headers que imitam um browser real
        'http_headers': {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/125.0.0.0 Safari/537.36'
            ),
        },
    }

    for i, url in enumerate(urls, 1):
        _info(f'[{i}/{len(urls)}] {url}')
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        if rate_limit and i < len(urls):
            delay = random.uniform(6, 14)
            _info(f'Rate limit: aguardando {delay:.1f}s...')
            time.sleep(delay)


# ---------------------------------------------------------------------------
# Transcrição — faster-whisper
# ---------------------------------------------------------------------------

def transcribe_faster_whisper(model_name: str, course_name: str, image_url: str):
    import torch
    from faster_whisper import WhisperModel

    device       = 'cuda' if torch.cuda.is_available() else 'cpu'
    compute_type = 'float16' if device == 'cuda' else 'int8'

    _info(f'Dispositivo: {device} | compute_type: {compute_type}')
    _info(f'Carregando modelo {model_name}...')
    model = WhisperModel(model_name, device=device, compute_type=compute_type)

    mp3_files = sorted(AUDIOS_DIR.glob('*.mp3'))
    if not mp3_files:
        _err('Nenhum MP3 encontrado.')
        sys.exit(1)

    results = []
    for idx, mp3 in enumerate(mp3_files, 1):
        _info(f'[{idx}/{len(mp3_files)}] Transcrevendo {mp3.name}...')
        segments, _ = model.transcribe(str(mp3), beam_size=5, language='pt')
        text = ''.join(seg.text for seg in segments).strip()
        results.append({
            'file_name': mp3.name,
            'course':    course_name,
            'topic':     mp3.stem,
            'transcription': text,
            'image':     image_url,
        })
        _info(f'  {len(text)} caracteres transcritos.')

    TRANSCRIPTION_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRANSCRIPTION_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    _done(f'Transcricao salva em {TRANSCRIPTION_FILE.name}')


# ---------------------------------------------------------------------------
# Transcrição — openai-whisper (fallback)
# ---------------------------------------------------------------------------

def transcribe_openai_whisper(model_name: str, course_name: str, image_url: str):
    from videos_transcriber import Transcriber

    t = Transcriber(model_name=model_name)
    t.audios_folder = str(AUDIOS_DIR)
    t.output_name   = str(TRANSCRIPTION_FILE)
    TRANSCRIPTION_DIR.mkdir(parents=True, exist_ok=True)
    t.transribe(course_name=course_name, image_url=image_url)


# ---------------------------------------------------------------------------
# Limpeza
# ---------------------------------------------------------------------------

def cleanup():
    _step('Limpando arquivos temporários...')
    if AUDIOS_DIR.exists():
        shutil.rmtree(AUDIOS_DIR)
        _done(f'audios/ removida.')
    if TRANSCRIPTION_FILE.exists():
        TRANSCRIPTION_FILE.unlink()
        _done('transcription.json removido.')


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------

def run(course, image_url, urls, backend, model, rate_limit, keep):
    print(f'\n{"="*58}')
    print(f'  Curso  : {course}')
    print(f'  Imagem : {image_url}')
    print(f'  Backend: {backend} | Modelo: {model}')
    print(f'  Rate limit: {"sim" if rate_limit else "não"}')
    print(f'  Vídeos : {len(urls)}')
    for u in urls:
        print(f'    • {u}')
    print(f'{"="*58}')

    # 1. Download
    _step(f'Baixando {len(urls)} vídeo(s) como MP3...')
    download_audios(urls, rate_limit=rate_limit)
    mp3s = list(AUDIOS_DIR.glob('*.mp3'))
    if not mp3s:
        _err('Nenhum MP3 foi baixado. Verifique as URLs.')
        sys.exit(1)
    _done(f'{len(mp3s)} arquivo(s) MP3 baixado(s).')

    # 2. Transcrição
    _step(f'Transcrevendo com {backend} ({model})...')
    if backend == 'faster-whisper':
        transcribe_faster_whisper(model, course, image_url)
    else:
        transcribe_openai_whisper(model, course, image_url)
    _done('Transcrição concluída.')

    # 3. Processar (parágrafos + video IDs)
    _step('Dividindo em parágrafos e associando IDs de vídeo...')
    processor = JsonProcessor(TRANSCRIPTION_FILE, DB_FILE)
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    processor.process(video_urls=urls)
    _done('Processamento concluído.')

    # 4. Salvar no data.json
    _step('Mesclando no data.json...')
    processor.put_in_db()
    _done('Dados salvos no data.json.')

    # 5. Limpeza
    if not keep:
        cleanup()

    print(f'\n{"="*58}')
    print(f'  Curso "{course}" adicionado com sucesso!')
    print(f'  Reinicie o backend para carregar os novos dados.')
    print(f'{"="*58}\n')


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Adiciona um curso ao data.json a partir de URLs do YouTube.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('--course',  '-c', required=True,
                        help='Nome do curso')
    parser.add_argument('--image',   '-i', required=True,
                        help='Imagem: nome em static/, caminho local ou URL')
    parser.add_argument('--backend', '-b', default='faster-whisper',
                        choices=['faster-whisper', 'whisper'],
                        help='Backend de transcrição (padrão: faster-whisper)')
    parser.add_argument('--model',   '-m', default='large-v3-turbo',
                        help='Modelo Whisper (padrão: large-v3-turbo)')
    parser.add_argument('--rate-limit', action='store_true',
                        help='Dorme 6-14s entre downloads para evitar bloqueio do YouTube')
    parser.add_argument('--keep',    action='store_true',
                        help='Mantém audios/ e transcription.json após processar')
    parser.add_argument('urls', nargs='+', metavar='URL',
                        help='URLs do YouTube')

    args = parser.parse_args()

    run(
        course     = args.course,
        image_url  = resolve_image(args.image),
        urls       = args.urls,
        backend    = args.backend,
        model      = args.model,
        rate_limit = args.rate_limit,
        keep       = args.keep,
    )


if __name__ == '__main__':
    main()
