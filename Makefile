all:
	cd ../ && ./noise.py build live
release: build
	cp -r build/* release/
	cd release && git add --all && git commit -m "Automatic build" && git push
