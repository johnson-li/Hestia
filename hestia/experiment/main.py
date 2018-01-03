import json
import re

import httplib
import paramiko

from hestia import RESOURCE_PATH
from hestia.info.dpid import DPID
from hestia.info.mac import MAC

ssh_clients = {}


def get_ssh(host):
    if host in ssh_clients.keys():
        return ssh_clients[host]
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_config = paramiko.SSHConfig()
    with open(RESOURCE_PATH + '/ssh/config') as f:
        ssh_config.parse(f)
    cfg = ssh_config.lookup(host)
    ssh.connect(cfg['hostname'], username=cfg['user'], key_filename=cfg['identityfile'])
    ssh_clients[host] = ssh
    return ssh


def get_latency(host, peer):
    ssh = get_ssh(host)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(
        "ping -c 10 " + peer + " | tail -1| awk '{print $4}' | cut -d '/' -f 2")
    for line in ssh_stdout:
        return float(line)


def get_port(host, port_name):
    ssh = get_ssh(host)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("sudo ovs-ofctl show br1| grep '({})'".format(port_name))
    for line in ssh_stdout:
        return re.search('[0-9]+', line).group()


class StaticFlowPusher(object):

    def __init__(self, server):
        self.server = server

    def get(self, data):
        ret = self.rest_call({}, 'GET')
        return json.loads(ret[2])

    def set(self, data):
        ret = self.rest_call(data, 'POST')
        return ret[0] == 200

    def remove(self, objtype, data):
        ret = self.rest_call(data, 'DELETE')
        return ret[0] == 200

    def rest_call(self, data, action):
        path = '/wm/staticflowpusher/json'
        headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json',
        }
        body = json.dumps(data)
        conn = httplib.HTTPConnection(self.server, 8080)
        conn.request(action, path, body, headers)
        response = conn.getresponse()
        ret = (response.status, response.reason, response.read())
        conn.close()
        return ret


pusher = StaticFlowPusher('35.193.107.149')


def add_default_flows(all_regions):
    for region in all_regions:
        # router -> server
        flow = {
            'switch': DPID[region]['router'],
            'name': '{}-route-server-default'.format(region),
            'cookie': '0',
            'eth_type': '0x0800',
            'priority': '10',
            'in_port': get_port(region + '-router', 'eth1'),
            'active': 'true',
            'actions': 'output={}'.format(get_port(region + '-router', 'gre_server')),
        }
        print(flow)
        pusher.set(flow)
        # server -> local
        flow = {
            'switch': DPID[region]['server'],
            'name': '{}-server-default'.format(region),
            'cookie': '0',
            'eth_type': '0x0800',
            'priority': '200',
            'in_port': get_port(region + '-server', 'gre_router'),
            'active': 'true',
            'actions': 'set_field=ipv4_dst->10.10.10.10,set_field=eth_dst->{},output=local'.format(
                MAC[region]['server']['br1']),
        }
        print(flow)
        pusher.set(flow)


def add_flows(target, other_regions, peer_ip):
    # router -> router forwarding
    for other_region in other_regions:
        flow = {
            'switch': DPID[other_region]['router'],
            'name': 'route-{}-{}'.format(other_region, peer_ip),
            'cookie': '0',
            'eth_type': '0x0800',
            'ipv4_src': peer_ip,
            'priority': '100',
            'in_port': get_port(other_region + '-router', 'eth1'),
            'active': 'true',
            'actions': 'output={}'.format(get_port(other_region + '-router', 'gre_' + target)),
        }
        pusher.set(flow)
        print(flow)
    # router(eth) -> server forwarding
    flow = {
        'switch': DPID[target]['router'],
        'name': 'route-{}-{}'.format(target, peer_ip),
        'cookie': '0',
        'eth_type': '0x0800',
        'ipv4_src': peer_ip,
        'priority': '200',
        # 'in_port': get_port(target + '-router', 'eth1'),
        'active': 'true',
        'actions': 'output={}'.format(get_port(target + '-router', 'gre_server')),
    }
    print(flow)
    pusher.set(flow)
    # router(gre) -> server forwarding
    flow = {
        'switch': DPID[target]['router'],
        'name': 'route-{}'.format(peer_ip),
        'cookie': '0',
        'eth_type': '0x0800',
        'ipv4_src': peer_ip,
        'priority': '100',
        'in_port': get_port(target + '-router', 'eth1'),
        'active': 'true',
        'actions': 'output={}'.format(get_port(target + '-router', 'gre_server')),
    }
    print(flow)
    pusher.set(flow)


peer = '35.193.107.149'

if __name__ == '__main__':
    regions = ['tokyo', 'sydney', 'singapore']
    add_default_flows(regions)
    results = []
    # for region in regions:
    #     results.append((region, get_latency(region + "-server", peer)))
    # results.sort(key=lambda pair: pair[1])
    results = [('tokyo', 126.537), ('sydney', 173.48), ('singapore', 189.041)]
    print(results)
    add_flows(results[0][0], [i[0] for i in results[1:]], peer)