.PHONY: build up down logs clean rebuild

build:
	docker compose build

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f loadbalancer

clean:
	docker compose down --rmi all -v
	-docker network rm net1

rebuild: clean up
