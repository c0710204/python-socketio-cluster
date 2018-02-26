import yaml
import time
import random
import subprocess
import uuid
import logging
import argparse
from multiprocessing import Process
fmt = "[%(asctime)-15s][%(levelname)s][%(filename)s:%(lineno)d][%(process)d]%(message)s"
datefmt = "%a %d %b %Y %H:%M:%S"
logging.basicConfig(format=fmt, datefmt=datefmt, level=21)


class client():
    def __init__(self,
                 host,
                 username="root",
                 password=None,
                 port=22,
                 name=None):
        if name:
            self.uuid = name
        else:
            self.uuid = uuid.uuid4()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        # create transport
        self.transport = None


def ftunnel(*args):
    while (1):
        try:
            client = args[-1]
            cmd = "ssh -NL {0}:{1}:{2} {3}@{4} -p {5} >/dev/null".format(
                args[0], args[1], args[2], client.username, client.host,
                client.port)
            logging.info(cmd)
            ret = subprocess.call(cmd, shell=True)
            logging.warning("[connection][{}]return {},restarting...".format(
                client.uuid, ret))
            time.sleep(3)
        except Exception as e:
            logging.warning("[connection][{}]{}".format(client.uuid, e))


def rftunnel(*args):
    while (1):
        try:
            client = args[-1]
            cmd = "ssh -NR {0}:{1}:{2} {3}@{4} -p {5} >/dev/null".format(
                args[0], args[1], args[2], client.username, client.host,
                client.port)
            logging.info(cmd)
            ret = subprocess.call(cmd, shell=True)
            logging.warning("[connection][{}]return {},restarting...".format(
                client.uuid, ret))
            time.sleep(3)
        except Exception as e:
            # raise e
            logging.warning("[connection][{}]{}".format(client.uuid, e))


if __name__ == "__main__":
    # argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '-c',
        default="config/sdn.yaml",
        help='path of config file')

    args = parser.parse_args()

    clients = {}
    procs = []
    # read configs
    config = yaml.load(open(args['c'], 'r').read())
    for c in config['client']:
        clients[c['name']] = client(c['host'], c['username'], c['password'],
                                    c['port'], c['name'])
    inner_base = 43000
    for conn in config['connection']:
        if 'inner' in conn:
            inner = conn['inner']
        else:
            inner = random.randint(43000, 60000)

            # inner=inner_base
            inner_base += 1
        snd = Process(
            target=ftunnel,
            args=(inner, 'localhost', conn['to']['port'],
                  clients[conn['to']['server']]))
        rev = Process(
            target=rftunnel,
            args=(conn['from']['port'], 'localhost', inner,
                  clients[conn['from']['server']]))
        snd.daemon = True
        rev.daemon = True
        snd.start()
        rev.start()
        procs.append(snd)
        procs.append(rev)
        conn['pid'] = [snd, rev]
        logging.info("{0}:{1} =={4}==> {2}:{3}".format(
            conn['from']['server'], conn['from']['port'], conn['to']['server'],
            conn['to']['port'], inner))
    try:
        while 1:
            time.sleep(1)
    except Exception as e:
        logging.warning("Killing links...")
        for proc in procs:
            proc.terminate()
        logging.warning("Successfully exiting")
