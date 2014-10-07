build:
	cd ../ && ./noise.py build live
release: build
	cp -r build/* live/ && cd live
	git add --all && git commit -m "Automatic build" && git push
