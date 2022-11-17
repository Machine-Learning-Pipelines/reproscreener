wget https://github.com/kermitt2/grobid/archive/0.7.2.zip
unzip 0.7.2.zip
cd grobid-0.7.2
./gradlew clean install

./gradlew clean assemble
