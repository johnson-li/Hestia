import os
import json
import time
import zipfile
import paramiko
import subprocess
from pathlib import Path
from shutil import copyfile
from experiment.gcloud.config import *
from experiment.gcloud.logging import logging
from experiment.gcloud.gce_utils_multiplexing import GceUtilMul
from experiment.gcloud.gce_utils import instances_already_created, get_instance_zone, get_external_ip

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PROJECT_PATH = os.path.dirname(os.path.dirname(DIR_PATH))
CONCURRENCY = 10
logger = logging.getLogger('main')
ZONE_NUMBERS = len(ZONES)
zones = ZONES[:ZONE_NUMBERS]
gce_util_mul = GceUtilMul(concurrency=CONCURRENCY, zones=zones)
INIT_GCLOUD = True


def zip_data():
    zip_file = zipfile.ZipFile('%s/data2.zip' % DIR_PATH, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk('%s/data2' % DIR_PATH):
        for file in files:
            zip_file.write(os.path.join(root, file), arcname=os.path.join(root[len(DIR_PATH) + 1:], file))
    zip_file.close()


def prepare_data():
    Path(f'{DIR_PATH}/data2').mkdir(parents=False, exist_ok=True)
    copyfile('%s/ngtcp2/examples/client' % os.path.dirname(PROJECT_PATH), '%s/data2/client' % DIR_PATH)
    copyfile('%s/ngtcp2/examples/server' % os.path.dirname(PROJECT_PATH), '%s/data2/server' % DIR_PATH)
    copyfile('%s/ngtcp2-old/examples/client' % os.path.dirname(PROJECT_PATH), '%s/data2/client_transport' % DIR_PATH)
    copyfile('%s/ngtcp2-old/examples/server2' % os.path.dirname(PROJECT_PATH), '%s/data2/server_transport' % DIR_PATH)
    copyfile('%s/ngtcp2-old/lib/.libs/libngtcp2.so.0' % os.path.dirname(PROJECT_PATH),
             '%s/data2/libngtcp2.so.0' % DIR_PATH)
    copyfile('%s/openssl/libssl.so.1.1' % os.path.dirname(PROJECT_PATH), '%s/data2/libssl.so.1.1' % DIR_PATH)
    copyfile('%s/openssl/libcrypto.so.1.1' % os.path.dirname(PROJECT_PATH), '%s/data2/libcrypto.so.1.1' % DIR_PATH)
    zip_data()


def get_instances():
    return gce_util_mul.get_instances()


def get_mac(instance):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ip = get_external_ip(instance)
    key = paramiko.RSAKey.from_private_key_file(os.path.expanduser('~/.ssh/id_rsa'))
    success = False
    while not success:
        try:
            client.connect(hostname=ip, username='johnsonli1993', port=22, pkey=key, allow_agent=False,
                           look_for_keys=False)
            success = True
        except Exception as _:
            time.sleep(1)

    name = instance['name']
    stdin, stdout, stderr = client.exec_command("cat /sys/class/net/ens4/address")
    mac1 = stdout.read().decode()[:-1]
    stdin, stdout, stderr = client.exec_command("cat /sys/class/net/ens5/address")
    mac2 = stdout.read().decode()[:-1]
    client.close()
    return mac1, mac2


def get_ip(instance):
    ex_ip = []
    in_ip = []
    for interface in instance['networkInterfaces']:
        for config in interface['accessConfigs']:
            if config['name'] == 'External NAT':
                ex_ip.append(config['natIP'])
        in_ip.append(interface['networkIP'])
    return ex_ip[0], in_ip[0], ex_ip[1], in_ip[1]


def prepare_instances():
    instances = get_instances()
    logging.info('existing instances: %s' % [i['name'] for i in instances])

    if not instances_already_created(zones, instances):
        gce_util_mul.create_instances(single=True)
        gce_util_mul.wait_for_instances_to_start()

    if INIT_GCLOUD:
        logger.info('Configure Google load balancing')
        for i in range(len(zones)):
            command = 'gcloud compute instance-groups unmanaged create ' + zones[i][:-2] + ' --zone ' + zones[i]
            command += ' > /dev/null'
            os.system(command)
            command = 'gcloud compute instance-groups set-named-ports ' + zones[i][
                                                                          :-2] + ' --named-ports tcp110:110 --zone ' + \
                      zones[i]
            command += ' > /dev/null'
            os.system(command)
            command = 'gcloud compute instance-groups unmanaged add-instances ' + zones[i][:-2] + ' --instances hestia-' + \
                      zones[i] + '-server --zone ' + zones[i]
            command += ' > /dev/null'
            os.system(command)

        command = 'gcloud compute health-checks create tcp health-check --port 110'
        command += ' > /dev/null'
        os.system(command)
        command = 'gcloud compute backend-services create load-balancer --global --protocol TCP ' \
                  '--health-checks health-check --timeout 5m --port-name tcp110'
        command += ' > /dev/null'
        os.system(command)

        for i in range(len(zones)):
            command = 'gcloud compute backend-services add-backend load-balancer --global --instance-group ' + \
                      zones[i][:-2] + ' --instance-group-zone ' + \
                      zones[i] + ' --balancing-mode UTILIZATION --max-utilization 0.8'
            command += ' > /dev/null'
            os.system(command)

        command = 'gcloud compute target-tcp-proxies create load-balancer-target-proxy ' \
                  '--backend-service load-balancer --proxy-header NONE'
        command += ' > /dev/null'
        os.system(command)
        command = 'gcloud compute addresses create load-balancer-static-ipv4 --ip-version=IPV4 --global'
        command += ' > /dev/null'
        os.system(command)

        s = os.popen('gcloud compute addresses list')
        ad_list = s.read()
        ad = ad_list.split()
        lb_ip = ''
        for i in range(len(ad)):
            if ad[i] == 'load-balancer-static-ipv4':
                lb_ip = ad[i + 1]

        command = 'gcloud beta compute forwarding-rules create load-balancer-ipv4-forwarding-rule --global ' \
                  '--target-tcp-proxy load-balancer-target-proxy --address ' + lb_ip + ' --ports 110'
        command += ' > /dev/null'
        os.system(command)
        command = 'gcloud compute firewall-rules create allow-load-balancer-and-health ' \
                  '--source-ranges 0.0.0.0/0 --allow tcp:110'
        command += ' > /dev/null'
        os.system(command)

    logger.info('Initiate database')
    instances = get_instances()
    lis = {}
    for i in instances:
        name = i['name']
        ex_ip1, in_ip1, ex_ip2, in_ip2 = get_ip(i)
        zone = get_instance_zone(i)
        mac1, mac2 = get_mac(i)
        lis[name] = {'external_ip1': ex_ip1, 'external_ip2': ex_ip2, 'internal_ip1': in_ip1, 'internal_ip2': in_ip2,
                     'mac1': mac1, 'mac2': mac2, 'zone': zone}

    s = os.popen('sudo mysql -e "show master status" -E| grep Position')
    position = s.read().strip()
    pos = position.split()
    lis['position'] = pos[1]
    s = os.popen('sudo mysql -e "show master status" -E| grep File')
    f = s.read().strip()
    fl = f.split()
    lis['file'] = fl[1]

    logger.info('Dump server info to machine.json')
    with open('machine.json', 'w', encoding='utf-8') as f:
        json.dump(lis, f, ensure_ascii=False)

    logger.info('Initiate instances')
    gce_util_mul.init_instances(execute_init_script=True, second_zip=True)
    logger.info('Initiate experiments')
    # gce_util_mul.init_experiment()
    return instances


def init_database(instances):
    subprocess.call(['%s/data2/init_db.sh' % DIR_PATH])


def conduct_experiment(instances):
    gce_util_mul.conduct_experiment(instances, second_zip=True)


def main():
    ts_start = time.time()
    prepare_data()
    instances = prepare_instances()
    logger.info('Initiate database')
    init_database(instances)
    logger.info('Conduct experiment')
    conduct_experiment(instances)
    logger.info(f"Starting servers takes {time.time() - ts_start:.2f} seconds")


if __name__ == '__main__':
    main()
