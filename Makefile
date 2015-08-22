########################################################
#
# Makefile for patchapp
#
# useful targets:
#   make run -- Collect static files, migrate db and run server.
#   make rundb -- Collect static files, migrate db, initialize db, and run server.
#
########################################################


NAME := patchapp
SRC := autopatch

clean:
	@rm -fR $(NAME)env

cleandb:
	@rm -f db.sqlite3

virtualenv:
	@echo "#############################################"
	@echo "# Creating a virtualenv"
	@echo "#############################################"
	virtualenv -p python3 $(NAME)env
	. $(NAME)env/bin/activate && pip install -r requirements.txt

setup:
	@echo "#############################################"
	@echo "# Collecting static files and migrating db"
	@echo "#############################################"
	. $(NAME)env/bin/activate && python3 manage.py collectstatic --noinput
	. $(NAME)env/bin/activate && python3 manage.py makemigrations
	. $(NAME)env/bin/activate && python3 manage.py migrate --noinput

pep8:
	@echo "#############################################"
	@echo "# Running PEP8 Compliance Tests in virtualenv"
	@echo "#############################################"
	. $(NAME)env/bin/activate && pep8 --ignore=E501,E121,E124 $(SRC)/

pyflakes:
	@echo "#############################################"
	@echo "# Running Pyflakes Sanity Tests in virtualenv"
	@echo "# Note: most import errors may be ignored"
	@echo "#############################################"
	. $(NAME)env/bin/activate && pyflakes $(SRC)

setupdb:
	@echo "#############################################"
	@echo "# Seeding database with test data"
	@echo "#############################################"
	sqlite3 db.sqlite3 < seed.sql

startserver:
	@echo "#############################################"
	@echo "# Starting server"
	@echo "#############################################"
	. $(NAME)env/bin/activate && python3 manage.py runserver 0.0.0.0:8080

run: clean virtualenv setup startserver

rundb: clean cleandb virtualenv setup setupdb startserver
