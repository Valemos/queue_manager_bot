run:
	heroku ps:scale worker=1

stop:
	heroku ps:scale worker=0

restart:
	make stop
	make run
