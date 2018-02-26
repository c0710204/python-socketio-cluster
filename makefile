ignore:
	echo ""

sdn:
	python server/sdn.py -c config/sdn.yaml

client:
	python pspnet/pspnet_serving.py

test_server:
	python pspnet/pspnet_serving_tester.py

prepare:
	scp -P 50022 guxi@star.eecs.oregonstate.edu:/home/guxi/tree2/pspnet/weights/keras/pspnet50_ade20k* ./pspnet/weights/keras/
