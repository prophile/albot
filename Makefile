all: ALYNN.zip

ALYNN.zip:
	rm -f ALYNN.zip
	zip ALYNN.zip robot.py
	zip -r ALYNN.zip albot/*.py

clean:
	rm -rf ALYNN.zip

.PHONY: all clean
