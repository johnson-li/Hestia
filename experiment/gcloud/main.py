import json
import os
import subprocess
import time
import zipfile
from shutil import copyfile, copytree

import paramiko

from experiment.gcloud.config import *
from experiment.gcloud.gce_utils import instances_already_created, get_instance_zone, get_external_ip
from experiment.gcloud.gce_utils_multiplexing import GceUtilMul
from experiment.gcloud.logging import logging

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.dirname(os.path.dirname(DIR_PATH))
CONCURRENCY = 10
ZONE_NUMBERS = len(ZONES)
#ZONE_NUMBERS = 2
zones = ZONES[:ZONE_NUMBERS]
restart_for_each_run = False
gce_util_mul = GceUtilMul(concurrency=CONCURRENCY, zones=zones)
logger = logging.getLogger('main')

logger.info('Concurrency: %d' % CONCURRENCY)
logger.info('Zones: %s' % str(zones))


def clean():
    gce_util_mul.delete_instances()


def get_instances():
    return gce_util_mul.get_instances()


def get_ip(instance):
    ex_ip = []
    in_ip = []
    for interface in instance['networkInterfaces']:
        for config in interface['accessConfigs']:
            if config['name'] == 'External NAT':
                ex_ip.append(config['natIP'])
        in_ip.append(interface['networkIP'])
    return ex_ip[0], in_ip[0], ex_ip[1], in_ip[1]


def get_mac(instance):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ip = get_external_ip(instance)
    key = paramiko.RSAKey.from_private_key_file(os.path.expanduser('~/.ssh/id_rsa'))
    success = False
    while not success:
        try :
            client.connect(hostname=ip, username='aerberzhou', port=22, pkey=key, allow_agent=False, look_for_keys=False)
            success = True
        except :
            time.sleep(1)

    name = instance['name']
    stdin, stdout, stderr = client.exec_command("cat /sys/class/net/ens4/address")
    mac1 = stdout.read().decode()[:-1]
    stdin, stdout, stderr = client.exec_command("cat /sys/class/net/ens5/address")
    mac2 = stdout.read().decode()[:-1]
    client.close()
    return mac1, mac2


def prepare_instances():
    instances = get_instances()
    logging.info('existing instances: %s' % [i['name'] for i in instances])

    if instances_already_created(zones, instances):
        if restart_for_each_run:
            gce_util_mul.stop_instances()
            gce_util_mul.start_instances()
            gce_util_mul.wait_for_instances_to_start()
    else:
        # gce_util_mul.delete_instances()
        # gce_util_mul.wait_for_instances_to_delete()
        gce_util_mul.create_instances()
        gce_util_mul.wait_for_instances_to_start()

    for i in range(len(zones)):
        command = 'gcloud compute instance-groups unmanaged create ' + zones[i][:-2] + ' --zone ' + zones[i]
        command += ' > /dev/null 2>&1'
        os.system(command)
        command = 'gcloud compute instance-groups set-named-ports ' + zones[i][
                                                                      :-2] + ' --named-ports tcp110:110 --zone ' + \
                  zones[i]
        command += ' > /dev/null 2>&1'
        os.system(command)
        command = 'gcloud compute instance-groups unmanaged add-instances ' + zones[i][:-2] + ' --instances hestia-' + \
                  zones[i] + '-router --zone ' + zones[i]
        command += ' > /dev/null 2>&1'
        os.system(command)

    command = 'gcloud compute health-checks create tcp health-check --port 110'
    command += ' > /dev/null 2>&1'
    os.system(command)
    command = 'gcloud compute backend-services create load-balancer --global --protocol TCP --health-checks health-check --timeout 5m --port-name tcp110'
    command += ' > /dev/null 2>&1'
    os.system(command)

    for i in range(len(zones)):
        command = 'gcloud compute backend-services add-backend load-balancer --global --instance-group ' + zones[i][
                                                                                                           :-2] + ' --instance-group-zone ' + \
                  zones[i] + ' --balancing-mode UTILIZATION --max-utilization 0.8'
        command += ' > /dev/null 2>&1'
        os.system(command)

    command = 'gcloud compute target-tcp-proxies create load-balancer-target-proxy --backend-service load-balancer --proxy-header NONE'
    command += ' > /dev/null 2>&1'
    os.system(command)
    command = 'gcloud compute addresses create load-balancer-static-ipv4 --ip-version=IPV4 --global'
    command += ' > /dev/null 2>&1'
    os.system(command)

    s = os.popen('gcloud compute addresses list')
    ad_list = s.read()
    ad = ad_list.split()
    lb_ip = ''
    for i in range(len(ad)):
        if ad[i] == 'load-balancer-static-ipv4':
            lb_ip = ad[i + 1]

    command = 'gcloud beta compute forwarding-rules create load-balancer-ipv4-forwarding-rule --global --target-tcp-proxy load-balancer-target-proxy --address ' + lb_ip + ' --ports 110'
    command += ' > /dev/null 2>&1'
    os.system(command)
    command = 'gcloud compute firewall-rules create allow-load-balancer-and-health --source-ranges 0.0.0.0/0 --allow tcp:110'
    command += ' > /dev/null 2>&1'
    os.system(command)

    instances = get_instances()
    lis = {}
    for i in instances:
        name = i['name']
        ex_ip1, in_ip1, ex_ip2, in_ip2 = get_ip(i)
        zone = get_instance_zone(i)
        mac1, mac2 = get_mac(i)
        lis[name] = {'external_ip1': ex_ip1, 'external_ip2': ex_ip2, 'internal_ip1': in_ip1, 'internal_ip2': in_ip2,
                     'mac1': mac1, 'mac2': mac2, 'zone': zone}

    s = os.popen('sudo mysql -e "show master status\G" | grep Position')
    position = s.read()
    pos = position.split()
    lis['position'] = pos[1]
    s = os.popen('sudo mysql -e "show master status\G" | grep File')
    f = s.read()
    fl = f.split()
    lis['file'] = fl[1]

    with open('machine.json', 'w', encoding='utf-8') as f:
        json.dump(lis, f, ensure_ascii=False)

    logger.info('Initiate instances')
    gce_util_mul.init_instances(execute_init_script=True)
    logger.info('Initiate experiments')
    # gce_util_mul.init_experiment()
    return instances


def conduct_experiment(instances):
    gce_util_mul.conduct_experiment(instances)


def prepare_data():
    copyfile('%s/ngtcp2/examples/client' % os.path.dirname(PROJECT_PATH), f'{DIR_PATH}/data/client')
    copyfile('%s/ngtcp2/examples/server' % os.path.dirname(PROJECT_PATH), f'{DIR_PATH}/data/server')
    copyfile('%s/ngtcp2/examples/client' % os.path.dirname(PROJECT_PATH), f'{DIR_PATH}/data/client_transport')
    copyfile('%s/ngtcp2/examples/server' % os.path.dirname(PROJECT_PATH), f'{DIR_PATH}/data/server_transport')
    copyfile('%s/ngtcp2/examples/balancer2' % os.path.dirname(PROJECT_PATH), f'{DIR_PATH}/data/balancer2')
    # copytree('%s/ngtcp2/websites' % os.path.dirname(PROJECT_PATH), '%s/data/websites' % DIR_PATH)
    zip_data()


def zip_data():
    zipf = zipfile.ZipFile('%s/data.zip' % DIR_PATH, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk('%s/data' % DIR_PATH):
        for file in files:
            zipf.write(os.path.join(root, file), arcname=os.path.join(root[len(DIR_PATH) + 1:], file))
    zipf.close()


def init_database(instances):
    subprocess.call(['%s/data/init_db.sh' % DIR_PATH])
    # TODO: init database in the routers


def main():
    start = time.time()
    instances = {}
    prepare_data()
    # clean()
    instances = prepare_instances()
    init_database(instances)
    conduct_experiment(instances)
    end = time.time()
    print("time: ", end - start)


if __name__ == '__main__':
    main()
