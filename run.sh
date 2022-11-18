# eval "$(conda shell.bash hook)"
# conda activate repro-screener
if (( $(ps ax | grep [g]robid-service | wc -l) == 0 ))
then
    cd ../grobid-installation
    ./grobid-service/bin/grobid-service &>/dev/null &
    cd -
fi
poetry run python ./src/scrape_arxiv.py

