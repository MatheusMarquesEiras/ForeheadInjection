#!/usr/bin/env python3
"""
CLI para adicionar cursos ao data.json automaticamente.

Uso básico:
  python tools/cli.py --course "Python" --image python.png URL1 URL2 ...

Exemplos:
  # Imagem já em backend/static/
  python tools/cli.py --course "Python" --image python.png \\
      https://youtu.be/abc123 https://youtu.be/def456

  # Imagem em outro diretório (copiada automaticamente para backend/static/)
  python tools/cli.py --course "React" --image /home/user/react.png \\
      https://youtu.be/xyz789

  # Usar modelo Whisper maior para melhor qualidade
  python tools/cli.py --course "Java" --image java.png --model turbo \\
      https://youtu.be/aaa111

  # Manter arquivos temporários (audios + transcription.json) após processar
  python tools/cli.py --course "C" --image clang.png --keep \\
      https://youtu.be/bbb222

Modelos Whisper disponíveis (em ordem de velocidade/qualidade):
  tiny, base, small, medium, large, turbo
"""

import argparse
import shutil
import sys
from pathlib import Path

# Resolve caminhos a partir da localização deste arquivo,
# funcionando corretamente de qualquer diretório de trabalho.
TOOLS_DIR = Path(__file__).parent.resolve()
ROOT = TOOLS_DIR.parent.resolve()

AUDIOS_DIR        = ROOT / 'audios'
TRANSCRIPTION_DIR = ROOT / 'transcription'
TRANSCRIPTION_FILE = TRANSCRIPTION_DIR / 'transcription.json'
DB_FILE           = ROOT / 'backend' / 'data.json'
STATIC_DIR        = ROOT / 'backend' / 'static'

sys.path.insert(0, str(TOOLS_DIR))

from download_audio import video_downloader
from videos_transcriber import Transcriber
from processJson import JsonProcessor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def resolve_image(image_arg: str) -> str:
    """
    Aceita:
      - URL completa (http/https) → retorna como está
      - Nome de arquivo (ex: python.png) → assume que já está em backend/static/
      - Caminho local de arquivo → copia para backend/static/ e retorna URL
    """
    if image_arg.startswith('http://') or image_arg.startswith('https://'):
        return image_arg

    candidate = Path(image_arg)

    # Caminho absoluto ou relativo que existe
    if candidate.exists():
        STATIC_DIR.mkdir(parents=True, exist_ok=True)
        dest = STATIC_DIR / candidate.name
        if candidate.resolve() != dest.resolve():
            shutil.copy(candidate, dest)
            _done(f"Imagem copiada para {dest}")
        return f'http://localhost:5000/static/{candidate.name}'

    # Nome simples — assume que já está em static/
    return f'http://localhost:5000/static/{image_arg}'


def _step(msg: str):
    print(f'\n\033[1;34m[→]\033[0m {msg}')


def _done(msg: str):
    print(f'\033[1;32m[✓]\033[0m {msg}')


def _err(msg: str):
    print(f'\033[1;31m[✗]\033[0m {msg}', file=sys.stderr)


def _cleanup():
    _step('Limpando arquivos temporários...')
    if AUDIOS_DIR.exists():
        shutil.rmtree(AUDIOS_DIR)
        _done(f'Pasta {AUDIOS_DIR.name}/ removida.')
    if TRANSCRIPTION_FILE.exists():
        TRANSCRIPTION_FILE.unlink()
        _done('transcription.json removido.')


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run(course: str, image_url: str, urls: list[str], model: str, keep: bool):
    print(f'\n{"="*55}')
    print(f'  Curso : {course}')
    print(f'  Imagem: {image_url}')
    print(f'  Modelo: {model}')
    print(f'  URLs  : {len(urls)} vídeo(s)')
    for u in urls:
        print(f'    • {u}')
    print(f'{"="*55}')

    # 1. Download
    _step(f'Baixando {len(urls)} vídeo(s) como MP3...')
    AUDIOS_DIR.mkdir(parents=True, exist_ok=True)
    video_downloader(video_urls=urls, pasta_destino=str(AUDIOS_DIR))
    _done('Download concluído.')

    mp3_count = len(list(AUDIOS_DIR.glob('*.mp3')))
    if mp3_count == 0:
        _err('Nenhum MP3 foi baixado. Verifique as URLs e tente novamente.')
        sys.exit(1)
    print(f'     {mp3_count} arquivo(s) MP3 encontrado(s).')

    # 2. Transcrição
    _step(f'Transcrevendo com Whisper ({model})...')
    TRANSCRIPTION_DIR.mkdir(parents=True, exist_ok=True)

    transcriber = Transcriber(model_name=model)
    transcriber.audios_folder = str(AUDIOS_DIR)
    transcriber.output_name = str(TRANSCRIPTION_FILE)
    transcriber.transribe(course_name=course, image_url=image_url)
    _done('Transcrição concluída.')

    # 3. Processar JSON (dividir em parágrafos + associar IDs dos vídeos)
    _step('Dividindo transcrições em parágrafos e associando vídeos...')
    processor = JsonProcessor(TRANSCRIPTION_FILE, DB_FILE)
    processor.process(video_urls=urls)
    _done('Processamento concluído.')

    # 4. Salvar no data.json
    _step('Mesclando dados no data.json...')
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    processor.put_in_db()
    _done('Dados salvos no data.json.')

    # 5. Limpeza
    if not keep:
        _cleanup()

    print(f'\n\033[1;32m{"="*55}')
    print(f'  Curso "{course}" adicionado com sucesso!')
    print(f'  Reinicie o backend para carregar os novos dados.')
    print(f'{"="*55}\033[0m\n')


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Adiciona um curso ao data.json a partir de URLs do YouTube.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        '--course', '-c', required=True,
        help='Nome do curso (ex: "Python Básico")',
    )
    parser.add_argument(
        '--image', '-i', required=True,
        help='Imagem do curso: nome do arquivo em static/, caminho local, ou URL completa',
    )
    parser.add_argument(
        '--model', '-m', default='turbo',
        choices=['tiny', 'base', 'small', 'medium', 'large', 'turbo'],
        help='Modelo Whisper (padrão: turbo)',
    )
    parser.add_argument(
        '--keep', action='store_true',
        help='Mantém audios/ e transcription.json após processar',
    )
    parser.add_argument(
        'urls', nargs='+', metavar='URL',
        help='URLs do YouTube (uma ou mais)',
    )

    args = parser.parse_args()
    image_url = resolve_image(args.image)

    run(
        course=args.course,
        image_url=image_url,
        urls=args.urls,
        model=args.model,
        keep=args.keep,
    )


if __name__ == '__main__':
    main()
