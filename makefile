ignore:
	echo ""

sdn:
	python server/sdn.py -c config/sdn.yaml

client:
	python pspnet/pspnet_serving.py

test_server:
	python pspnet/pspnet_serving_tester.py

prepare:
	mkdir -p ./pspnet/weights/keras/
	scp -P 50022 guxi@127.0.0.1:/home/guxi/tree2/pspnet/weights/keras/pspnet50_ade20k* ./pspnet/weights/keras/
