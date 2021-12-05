all: build run rmi

build:
	docker-compose build web

export:
	docker save -o paddington.docker paddington

up:
	. ./.env && docker-compose up

run:
	. ./.env && docker-compose up -d

down:
	docker-compose down

rmi:
	docker image prune -f && docker volume prune -f
