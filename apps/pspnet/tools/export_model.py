# target: export keras model we used as tensorflow model
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
import os
import os.path as osp
from keras import backend as K

import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
config.gpu_options.per_process_gpu_memory_fraction = 0.499
sess = tf.Session(config=config)
set_session(sess)
import sys
sys.path.append('.')
from apps.pspnet.pkg.pspnet import deeplearning as dpl
from apps.pspnet.pkg.pspnet.psp_tf.pspnet import PSPNet50

model=PSPNet50(
            nb_classes=150,
            input_shape=(473, 473),
            weights="pspnet50_ade20k",
            path="./pspnet/weights")

net_model=model.model
print('input is :', net_model.input.name)
print ('output is:', net_model.output.name)
output_graph_name = 'tensor_model.pb'

output_fld =  './tensorflow_model/'

def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
    """
    Freezes the state of a session into a prunned computation graph.

    Creates a new computation graph where variable nodes are replaced by
    constants taking their current value in the session. The new graph will be
    prunned so subgraphs that are not neccesary to compute the requested
    outputs are removed.
    @param session The TensorFlow session to be frozen.
    @param keep_var_names A list of variable names that should not be frozen,
                          or None to freeze all the variables in the graph.
    @param output_names Names of the relevant graph outputs.
    @param clear_devices Remove the device directives from the graph for better portability.
    @return The frozen graph definition.
    """
    from tensorflow.python.framework.graph_util import convert_variables_to_constants
    graph = session.graph
    with graph.as_default():
        freeze_var_names = list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
        output_names = output_names or []
        output_names += [v.op.name for v in tf.global_variables()]
        input_graph_def = graph.as_graph_def()
        if clear_devices:
            for node in input_graph_def.node:
                node.device = ""
        frozen_graph = convert_variables_to_constants(session, input_graph_def,
                                                      output_names, freeze_var_names)
        return frozen_graph

frozen_graph = freeze_session(K.get_session(), output_names=[net_model.output.op.name])
from tensorflow.python.framework import graph_io
graph_io.write_graph(frozen_graph, output_fld, output_graph_name, as_text=False)
print('saved the constant graph (ready for inference) at: ', osp.join(output_fld, output_graph_name))