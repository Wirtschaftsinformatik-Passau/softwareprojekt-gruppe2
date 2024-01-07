postgres-volume:
	sudo docker volume create postgres-volume

postgres:
	sudo docker run --name postgres_tose_backend -p 5432:5432 -v postgres-volume:/var/lib/postgresql-volume/data -e POSTGRES_USER=root -e POSTGRES_PASSWORD=secret -d postgres:12-alpine

createdb:
	sudo docker exec -it postgres_tose_backend createdb --username=root --owner=root tose


dropdb:
	sudo docker exec -it postgres_tose_backend dropdb tose_backend

alembic-init:
	alemibic init alembic tose_backend


alembic-revision:
	alembic revision --autogenerate -m "Add new changes"

alembic-upgrade:
	alembic upgrade head

alembic-downgrade:
	alembic downgrade base

alembic-downgrade-1:
	alembic downgrade -1

alembic-upgrade-1:
	alembic upgrade +1

fill-users:
	python3 ./test/fill_with_users.py

fill-adress:
	python3 ./test/fill_with_adress.py

fill-tarif:
	python3 ./test/fill_with_tarifs.py

fill-price:
	python3 ./test/fill_with_prices.py

docker-network:
	sudo docker network create tose_network

start-postgres:
	sudo docker start postgres_tose_backend

alembic-volume:
	sudo docker volume create alembic-volume

inspect-backend:
	sudo docker exec -it fastapi-backend bash

log-backend:
	sudo docker logs fastapi-backend

inspect-alembic-volume:
	sudo docker run --rm -i -v=alembic-volume:/tmp/myvolume busybox find /tmp/myvolume