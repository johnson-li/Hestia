from experiment.gcloud.gce_utils import create_instance, ZONES
from experiment.gcloud.gce_utils_multiplexing import GceUtilMul
from experiment.gcloud.gce_utils import instances_already_created, get_instance_zone, get_external_ip
import json
import sys

ZONES_ALL = ['us-east1-c', 'us-east4-c', 'us-central1-c', 'us-west1-c', 'us-west2-c', 'us-west3-c',
             'europe-west1-c', 'europe-west2-c', 'europe-west3-c', 'europe-west4-c', 'europe-west6-c',
             'europe-north1-c',
             'asia-east1-c', 'asia-east2-c', 'asia-southeast1-c', 'asia-northeast1-c', 'asia-northeast2-c',
             'asia-northeast3-c', 'asia-south1-c', 'australia-southeast1-c',
             'southamerica-east1-c', 'northamerica-northeast1-c']

# zones = []
# for z in ZONES_ALL:
#     if z not in ZONES:
#         zones.append(z)
# zones = ['us-west4-c']
print(sys.argv)
zones = [ZONES_ALL[int(sys.argv[1])]]
print(zones)

CONCURRENCY = 10
gce_util_mul = GceUtilMul(concurrency=CONCURRENCY, zones=zones)

def get_instances():
    return gce_util_mul.get_instances()


def get_ip(instance):
    ex_ip = []
    in_ip = []
    for interface in instance['networkInterfaces']:
        for config in interface['accessConfigs']:
            if config['name'] == 'External NAT':
                try:
                    ex_ip.append(config['natIP'])
                except:
                    pass
    return ex_ip[0], ex_ip[1]
#        try:
#            in_ip.append(interface['networkIP'])
#        except:
#            pass
#    return ex_ip[0], in_ip[0], ex_ip[1], in_ip[1]


def main():
    instances = get_instances()
    print('existing_instances:', instances)

    flag_exist = 0
    existing_client_zone = []
    for i in instances:
        name = i['name']
        if 'client' in name:
            print('existing instances')
            # TODO, 将instance的zone 添加到existing_client_zone
            existing_client_zone.append(i['zone'].split('/')[-1])
            flag_exist = 1

    if flag_exist:
        gce_util_mul.delete_client_instances(client_zone=existing_client_zone)
        gce_util_mul.wait_for_client_instances_to_delete(client_zone=existing_client_zone)

    print('Zones: %s' % zones)
    instances = []
    for zone in zones:
        instances.append(create_instance(zone, 'client-%s' % zone))
    print(instances)


def check_hosts():
    instances = get_instances()
    lis = []

    f_hosts = open('experiment/client/data/hosts.json', 'r', encoding='utf-8')
    load_dict = json.load(f_hosts)
    print(load_dict)
    existing_hosts = [i['hostname'] for i in load_dict]

    for i in instances:
        name = i['name']
        if 'client' in name:
            if name not in existing_hosts:
                return False

    return True


def create_hosts():
    instances = get_instances()
    lis = []
    for i in instances:
        name = i['name']
        if 'client' in name:
            try:
                ex_ip1, ex_ip2 = get_ip(i)
                lis.append ({'hostname': ex_ip1, 'username': 'aerberzhou'})
            except:
                print('some lost in hosts.json, pls check!')
                pass

    with open('experiment/client/data/hosts.json', 'w', encoding='utf-8') as f:
        json.dump(lis, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
    while(check_hosts()):
        create_hosts()
