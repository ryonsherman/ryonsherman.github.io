all:
	cd static/etc/css && sass --style compressed app.sass > app.min.css && sass app.sass > app.css && rm -rf .sass-cache
	cd ../ && ./noise.py build live
release: all
	cp -r build/* release/
	cd release && git add --all && git commit -m "Automatic build" && git push
