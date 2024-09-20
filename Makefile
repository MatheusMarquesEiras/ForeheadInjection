all: run

run:
	cls
	flet run --web --port 8000 app

install:
	python -m venv venv
	venv/script/activate
	pip install -r requirements.txt