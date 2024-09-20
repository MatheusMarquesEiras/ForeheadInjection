all: run

run:
	cls
	flet run --web --port 8000 app

build:
	cd docker && docker compose up -d

install:
	python -m venv venv
	venv/script/activate
	pip install -r requirements.txt

clean:
	cd docker && docker compose down