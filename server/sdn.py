import yaml
import time
import random
import subprocess
import uuid
import logging
import argparse
from multiprocessing import Process

from src.libs.conf.conf import conf as conf

fmt = "[%(asctime)-15s][%(levelname)s][%(filename)s:%(lineno)d][%(process)d]%(message)s"
datefmt = "%a %d %b %Y %H:%M:%S"
logging.basicConfig(format=fmt, datefmt=datefmt, level=11)


class client():
    def __init__(self,
                 host,
                 username="root",
                 password=None,
                 port=22,
                 name=None):
        self.uuid = ""
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
            client_loc = args[-1]
            cmd = "ssh -NL {0}:{1}:{2} {3}@{4} -p {5} >/dev/null 2>&1".format(
                args[0], args[1], args[2], client_loc.username, client_loc.host,
                client_loc.port)
            logging.debug(cmd)
            ret = subprocess.call(cmd, shell=True)
            logging.warning("[connection][{}]return {},restarting...".format(
                client_loc.uuid, ret))
            time.sleep(3)
        except Exception as e:
            logging.warning("[connection][{}]{}".format(client_loc.uuid, e))


def rftunnel(*args):
    while (1):
        try:
            client_loc = args[-1]
            cmd = "ssh -NR {0}:{1}:{2} {3}@{4} -p {5} >/dev/null 2>&1".format(
                args[0], args[1], args[2], client_loc.username, client_loc.host,
                client_loc.port)
            logging.debug(cmd)
            ret = subprocess.call(cmd, shell=True)
            logging.warning("[connection][{}]return {},restarting...".format(
                client_loc.uuid, ret))
            time.sleep(3)
        except Exception as e:
            # raise e
            logging.warning("[connection][{}]{}".format(client_loc.uuid, e))


if __name__ == "__main__":
    # argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '-c',
        '--config',
        type=str,
        default="config/sdn.yaml",
        help='path of config file')

    args = parser.parse_args()

    clients = {}
    procs = []
    # read configs
    confloader = conf()
    confloader.load("sdn", args.config)
    confloader.load("service")
    config = confloader.sdn
    config_s = confloader.service
    config_connection = []
    if 'proxy' in config:
        for server_node_type in config['proxy']['service']:
            service_info_list = config['proxy']['service'][server_node_type]

            for service in service_info_list:
                server_port = config_s['services'][service['type']]['port']
                client_port = config_s['services'][service['type']]['port']
                client_list = config['client_type'][service['avaliable']]
                if 'port' in service:
                    server_port = service['port']

                for node_client in client_list:
                    for node_server in config['client_type'][server_node_type]:
                        if len([x for x in config['client']if x['name']==node_server and x['type']=='local'])>0:
                            node_server='local'
                        if len([x for x in config['client']if x['name']==node_client and x['type']=='local'])>0:
                            node_client='local'
                        config_connection.append(
                            {
                                'from': {'server': node_client, 'port': client_port},
                                'to': {'server': node_server, 'port': server_port}
                            }
                        )

    for c in config['client']:
        if c['type']=='ssh':
            clients[c['name']] = client(c['host'], c['username'], c['password'],
                                    c['port'], c['name'])
    inner_base = 43000
    for conn in config_connection:  # config['connection']:
        if 'inner' in conn:
            inner = conn['inner']
        else:
            inner = random.randint(43000, 60000)

            # inner=inner_base
            inner_base += 1
        if conn['to']['server'] == 'local':
            inner = '====='
            rev = Process(
                target=rftunnel,
                args=(conn['from']['port'], 'localhost', conn['to']['port'],
                      clients[conn['from']['server']]))
            rev.daemon = True
            rev.start()
            procs.append(rev)
            conn['pid'] = [rev]
        elif conn['from']['server'] == 'local':
            inner = '====='
            rev = Process(
                target=ftunnel,
                args=(conn['from']['port'], 'localhost', conn['to']['port'],
                      clients[conn['to']['server']]))
            rev.daemon = True
            rev.start()
            procs.append(rev)
            conn['pid'] = [rev]
        else:
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
