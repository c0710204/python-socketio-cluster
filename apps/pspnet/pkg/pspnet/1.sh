rm ./p1/*
rm ./p2/*
rm /tmp/*.npy
#image="p00M5fJkOGJQ72fS8axowng"
image="p7Q5FXn_15q2rBwGCnsAP9w"
python pre_process.py -s -f -ms -i "/home/guxi/put/allComposites/County41005/$image.jpg" -o "./p1/$image.jpg"
python deeplearning.py -s -f -ms -i ./p1/ -o ./p2/
python img_combine2.py -s -f -ms -i "/home/guxi/put/allComposites/County41005/$image.jpg" -i2 "./p2/$image.jpg" -o "./p3/$image.jpg"


#cd ~/put/PSPNet-Keras-tensorflow;python pspnet.py -i "/home/guxi/put/allComposites/County41005/$image.jpg" -o "/home/guxi/tree2/pspnet/p3_old/$image.jpg" -s -f -ms
