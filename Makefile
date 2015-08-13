########################################################
#
# Makefile for patchapp
#
# useful targets:
#   make run -- Collect static files, migrate db and run server.
#
########################################################


NAME := patchapp

clean:
	@rm -fR $(NAME)env

run: clean virtualenv
	. $(NAME)env/bin/activate && python3 manage.py collectstatic --noinput
	. $(NAME)env/bin/activate && python3 manage.py migrate --noinput
	. $(NAME)env/bin/activate && python3 manage.py runserver 0.0.0.0:8080

virtualenv:
	@echo "#############################################"
	@echo "# Creating a virtualenv"
	@echo "#############################################"
	virtualenv -p python3 $(NAME)env
	. $(NAME)env/bin/activate && pip install -r requirements.txt
