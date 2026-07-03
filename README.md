# EducaMundo

Plataforma web de cursos com vídeo, transcrição e atividades práticas, voltada para pessoas de baixa renda que querem aprender programação e tecnologia. Desenvolvida por **Matheus Eiras** e **Ricardo Takeda** na disciplina de Práticas de Extensão.

---

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python · Flask · SQLAlchemy · SQLite |
| Frontend | React · Vite · Tailwind CSS · React Router |
| Transcrição | faster-whisper (`large-v3-turbo`) |
| Download | yt-dlp |
| Gerenciador de pacotes | uv |

---

## Funcionalidades

- Página de cursos com card de imagem para cada curso disponível
- Página de conteúdo com player do YouTube embutido, transcrição em parágrafos e atividade de múltipla escolha
- Sidebar de tópicos ordenada pela sequência correta dos vídeos
- Seed automático do banco a partir de `data.json` (idempotente — não duplica registros)
- CLI para ingestão de novos cursos diretamente do YouTube

### Cursos disponíveis (10 cursos · 42 tópicos)

`C` · `Python` · `Ollama` · `C++` · `PHP` · `React` · `Java` · `Web` · `Pygame` · `PostgreSQL`

---

## Estrutura do projeto

```
ForeheadInjection/
├── backend/
│   ├── run.py          # Flask API + modelos SQLAlchemy + seed automático
│   ├── data.json       # Fonte de verdade: cursos, tópicos, conteúdos, atividades
│   └── static/         # Imagens dos cursos servidas pelo Flask
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Courses.jsx   # Listagem de cursos
│   │   │   └── Content.jsx   # Player + transcrição + atividade
│   │   └── App.jsx
│   └── package.json
├── tools/
│   ├── cli.py              # CLI principal de ingestão de cursos
│   ├── processJson.py      # Divide transcrições em parágrafos e grava no data.json
│   └── videos_transcriber.py  # Wrapper do openai-whisper (fallback)
├── docker/
│   └── docker-compose.yml  # PostgreSQL opcional
├── pyproject.toml          # Dependências Python (uv)
└── uv.lock
```

---

## Instalação e execução local

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (`pip install uv`)
- FFmpeg no PATH (necessário para o CLI de ingestão)

### 1 · Backend

```bash
# Instalar dependências Python
uv sync

# Iniciar o servidor (cria o banco SQLite e faz o seed automaticamente)
python backend/run.py
```

O Flask sobe em `http://localhost:5000`. Na primeira execução cria `backend/cursos.db` e popula a partir de `data.json`.

### 2 · Frontend

```bash
cd frontend
npm install
npm run dev
```

O Vite sobe em `http://localhost:5173`.

---

## API (Flask)

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/get-courses` | Lista todos os cursos |
| GET | `/get-topics/<course_id>` | Tópicos do curso ordenados por sequência |
| GET | `/get-content/<topic_id>` | Conteúdos do tópico (vídeo + parágrafos) |
| GET | `/get-activity/<topic_id>` | Atividade de múltipla escolha do tópico |
| GET | `/static/<filename>` | Imagens dos cursos |

---

## CLI — Adicionar novos cursos

O CLI baixa vídeos do YouTube, transcreve com `faster-whisper`, divide em parágrafos e insere no `data.json`.

```bash
python tools/cli.py \
  --course "Nome do Curso" \
  --image imagem.png \
  --model large-v3-turbo \
  --rate-limit \
  URL1 URL2 URL3 ...
```

**Opções principais:**

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--course` / `-c` | obrigatório | Nome do curso |
| `--image` / `-i` | obrigatório | Nome em `static/`, caminho local ou URL |
| `--model` / `-m` | `large-v3-turbo` | Modelo Whisper |
| `--backend` / `-b` | `faster-whisper` | `faster-whisper` ou `whisper` |
| `--rate-limit` | desativado | Dorme 6–14 s entre downloads (anti-bot) |
| `--keep` | desativado | Mantém `audios/` e `transcription.json` após processar |

Após rodar o CLI, reinicie o backend — o seed idempotente insere apenas os novos registros.

---

## Documentação

Os documentos gerados para a disciplina estão em `docs/`.
