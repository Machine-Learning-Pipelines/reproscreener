source /home/adb/anaconda3/etc/profile.d/conda.sh
conda activate repro-screener
if (( $(ps ax | grep [g]robid-service | wc -l) == 0 ))
then
    cd ./grobid-installation
    ./grobid-service/bin/grobid-service &>/dev/null &
    cd ..
fi
python ./pipeline/scrape_arxiv.py

