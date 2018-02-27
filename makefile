ignore:
	echo ""

sdn:
	python server/sdn.py -c config/sdn.yaml

client:
	mkdir -p /dev/shm/guxi
	mkdir -p /dev/shm/guxi/p1
	mkdir -p /dev/shm/guxi/p2
	mkdir -p /dev/shm/guxi/p3
	mkdir -p /dev/shm/guxi/tmp
	python pspnet/pspnet_serving.py

test_server:
	python pspnet/pspnet_serving_tester.py
server:
	python server/server_root.py
prepare:
	mkdir -p ./pspnet/weights/keras/
	scp -P 50022 guxi@127.0.0.1:/home/guxi/tree2/pspnet/weights/keras/pspnet50_ade20k* ./pspnet/weights/keras/
