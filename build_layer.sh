mkdir lambda-maker
cd lambda-maker/
mkdir python
cd python/
pip3 install pcpi -t .
rm -rf *.dist-info
cd ..
zip -r PCPI-lambda-layer.zip python/
