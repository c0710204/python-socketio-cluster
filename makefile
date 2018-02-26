ignore:
	echo ""

sdn:
	python server/sdn.py

server:
	python pspnet/pspnet_serving.py
	
prepare:
	scp -P 50022 guxi@star.eecs.oregonstate.edu:/home/guxi/tree2/pspnet/weights/keras/pspnet50_ade20k* ./pspnet/weights/keras/
