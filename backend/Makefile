postgres-volume:
	sudo docker volume create postgres-volume

postgres:
	sudo docker run --name postgres_tose_backend -p 5432:5432 -v postgres-volume:/var/lib/postgresql-volume/data -e POSTGRES_USER=root -e POSTGRES_PASSWORD=secret -d postgres:12-alpine

createdb:
	sudo docker exec -it postgres_tose_backend createdb --username=root --owner=root tose_backend


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
	python ./test/fill_with_users.py

fill-adress:
	python ./test/fill_with_adress.py

fill-tarif:
	python ./test/fill_with_tarifs.py

fill-price:
	python ./test/fill_with_prices.py