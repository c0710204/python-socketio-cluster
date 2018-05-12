import argparse
import numpy as np
from scipy import misc, ndimage
import img_combine_func2
from os.path import splitext, join, isfile, basename
import utils
from socketIO_client import SocketIO, LoggingNamespace
import uuid


def img_combine2(args):
    if args.multi_scale:
        EVALUATION_SCALES = [0.5, 0.75, 1.0, 1.25, 1.5,
                             1.75]  # must be all floats!
        #EVALUATION_SCALES = [0.15, 0.25, 0.5]  # must be all floats!
    #fit test:
    EVALUATION_SCALES.reverse()
    img = misc.imread(args.input_path)
    #img = misc.imresize(img, 10)
    img_shape = img.shape
    pspnet = {}
    pspnet['input_shape'] = (473, 473)
    pspnet['model.outputs[0].shape[3]'] = 150

    def funchandler(inp):
        if len(inp) == 7:
            filename, ext = splitext(args.input_path2)
            return np.load("{0}_-123-_{5}_-123-_{1}_-123-_{2}_-123-_{3}_-123-_{4}_-123-_.npy".format(
                filename, inp[2], inp[3], inp[4], inp[5], inp[6]))

    return img_combine_func2.predict_multi_scale(funchandler, img_shape,
                                                 pspnet, EVALUATION_SCALES,
                                                 args.sliding, args.flip, args)


if __name__ == '__main__':
    remote_uuid = "{0}{1}".format(uuid.uuid4(), "_imagecombine")
    socketIO = SocketIO('localhost', 30091, LoggingNamespace)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m',
        '--model',
        type=str,
        default='pspnet50_ade20k',
        help='Model/Weights to use',
        choices=[
            'pspnet50_ade20k', 'pspnet101_cityscapes', 'pspnet101_voc2012'
        ])
    parser.add_argument(
        '-i',
        '--input_path',
        type=str,
        default='example_images/ade20k.jpg',
        help='Path the input image')
    parser.add_argument(
        '-i2',
        '--input_path2',
        type=str,
        default='example_images/ade20k.jpg',
        help='Path the iupperlevel')
    parser.add_argument(
        '-o', '--output_path', type=str, default='p1/', help='Path to output')
    parser.add_argument('--id', default="0")
    parser.add_argument(
        '-s',
        '--sliding',
        action='store_true',
        help=
        "Whether the network should be slided over the original image for prediction."
    )
    parser.add_argument(
        '-f',
        '--flip',
        action='store_true',
        help=
        "Whether the network should predict on both image and flipped image.")
    parser.add_argument(
        '-ms',
        '--multi_scale',
        action='store_true',
        help="Whether the network should predict on multiple scales.")
    args = parser.parse_args()
    args.remote_uuid = remote_uuid

    filename, ext = splitext(args.output_path)
    iname = basename(filename)
    #args.socketIO=socketIO
    socketIO.emit('update', {'id': iname, "phase": 3, 'val': -1, 'max': -1})
    socketIO.wait(seconds=1)
    img = misc.imread(args.input_path)
    img = misc.imresize(img, 10)
    class_scores = img_combine2(args)
    print(class_scores.shape)
    class_image = np.argmax(class_scores, axis=2)
    pm = np.max(class_scores, axis=2)
    colored_class_image = utils.color_class_image(class_image, args.model)
    #colored_class_image is [0.0-1.0] img is [0-255]
    alpha_blended = 0.5 * colored_class_image + 0.5 * img

    np.save(filename + ".npy", class_scores)
    misc.imsave(filename + "_seg" + ext, colored_class_image)
    #misc.imsave(filename + "_probs" + ext, pm)
    misc.imsave(filename + "_seg_blended" + ext, alpha_blended)
    #visualize_prediction(class_scores)
    l = [np.count_nonzero(class_image == i) for i in range(150)]
    l = np.array(l).astype(np.float) / (img.shape[0] * img.shape[1])
    with open("treecount3.txt", 'a+') as f:
        f.write("{0} {1}\n".format(filename, ','.join(map(str, l))))
    socketIO.emit('update', {'id': iname, "phase": 3, 'val': 1, 'max': 1})
    socketIO.wait(seconds=1)
