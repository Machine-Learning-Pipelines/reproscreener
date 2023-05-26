SRC = $(wildcard ../src/reproscreener/*.py)
DOC = $(patsubst ../src/reproscreener/%.py, ../doc/%.txt, $(SRC))

all: $(DOC)

../doc/%.txt: ../src/reproscreener/%.py
	-mkdir -p ../doc
	pydoc $< > $@

concat:
	cat ../doc/*.txt > ../doc/concat.txt

.PHONY: clean

clean:
	rm -rf ../doc
