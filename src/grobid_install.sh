wget https://github.com/kermitt2/grobid/archive/0.7.2.zip
unzip 0.7.2.zip
cd grobid-0.7.2
./gradlew clean install

./gradlew clean assemble
cd ../
mkdir grobid-installation
cd grobid-installation
unzip ../grobid/grobid-service/build/distributions/grobid-service-0.7.2.zip
mv grobid-service-0.7.2 grobid-service
unzip ../grobid/grobid-home/build/distributions/grobid-home-0.7.2.zip
./grobid-service/bin/grobid-service

git clone https://github.com/kermitt2/grobid_client_python
cd grobid_client_python
pyenv local repro-poetry
python setup.py install