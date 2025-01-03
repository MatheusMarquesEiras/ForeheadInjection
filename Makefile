all: clean build run

run:
	sleep 5
	clear
	flet run --web --port 8000 app

build:
	cd docker && docker-compose up -d

clean:
	cd docker && docker-compose down
	clear