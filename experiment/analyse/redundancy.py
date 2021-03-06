from experiment.analyse.zones import handle_region
import json
import matplotlib.patches as mpatches
import MySQLdb
import matplotlib.pyplot as plt
import os
import numpy as np
from hestia import PROJECT_PATH
from experiment.analyse.zones import decode, shorten

FONT_SIZE = 16
DATA_PATH = os.path.join(PROJECT_PATH, f'resources/exp5')
CLIENT_REGIONS = ['ap-northeast-1', 'ap-northeast-2', 'ap-south-1', 'ap-southeast-1',
                  'ap-southeast-2', 'ca-central-1', 'eu-central-1', 'eu-north-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
                  'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2']
SERVER_IP_MAP = {}


def init():
    data = json.load(open(os.path.join(DATA_PATH, "machine.json")))
    data = json.load(open(os.path.join(DATA_PATH, "machine2.json")))
    data = json.load(open(os.path.join(DATA_PATH, "machine3.json")))
    for k, v in data.items():
        if k.startswith('hestia'):
            SERVER_IP_MAP[v['external_ip1']] = '-'.join([''.join((t[:2], t[-2:])) for t in k[7:].split('-')[:2]])


def handle_region(name, last=False):
    print(f'Regions: {name}')
    latencies = {}
    db = MySQLdb.connect("127.0.0.1", "johnson", "johnson", "serviceid_db")
    db.query('select * from measurements order by ts')
    client_ip_mapping = {}
    r = db.store_result()
    while True:
        a = r.fetch_row()
        if not a:
            break
        a = a[0]
        _, server_region, client_ip, _, latency, _ = a
        latencies.setdefault(client_ip, {})[server_region] = latency
    db.query('select * from transfer_time')
    r = db.store_result()
    data = {}
    anycast_targets = {}
    sid_targets = {}
    while True:
        a = r.fetch_row()
        if not a:
            break
        a = a[0]
        item_id, client_ip, router_ip, server_ip, hostname, client_region, router_region, server_region, \
        service_id_transfer_time, service_id_handshake_time, dns_query_time, dns_transfer_time, \
        dns_handshake_time, anycast_transfer_time, anycast_handshake_time, service_plt_time, dns_plt_time, \
        anycast_plt_time, bind_server_ip, website, timestamp = [decode(i) for i in a]
        server_region = SERVER_IP_MAP[bind_server_ip]
        client_ip_mapping[client_ip] = client_region
        anycast_targets[client_region] = '-'.join([''.join((t[:2], t[-2:])) for t in router_region[7:].split('-')[:2]])
        sid_targets[client_region] = server_region
        data.setdefault(client_ip, {'hostname': hostname, 'client_region': client_region, 'records': []})
        data[client_ip]['records'].append({'router_ip': router_ip, 'server_ip': server_ip,
                                           'router_region': router_region, 'server_region': server_region,
                                           'sid_tf': service_id_transfer_time, 'sid_hs': service_id_handshake_time,
                                           'dns_query': dns_query_time, 'dns_tf': dns_transfer_time,
                                           'dns_hs': dns_handshake_time,
                                           'any_tf': anycast_transfer_time, 'any_hs': anycast_handshake_time,
                                           'sid_plt': service_plt_time, 'dns_plt': dns_plt_time,
                                           'any_plt': anycast_plt_time, 'bind_server_ip': bind_server_ip,
                                           'website': website, 'timestamp': timestamp})
    latencies = {client_ip_mapping[k]: v for k, v in latencies.items() if k in client_ip_mapping}
    rank = {}
    rank_r = [0] * len(latencies)
    rank_s = [0] * len(latencies)
    print(f'SID targets: {sid_targets}')
    for k, v in latencies.items():
        keys = list(v.keys())
        values = [v[kk] for kk in keys]
        i = np.argsort(values)
        rank[k] = [keys[ii] for ii in i]
    for k in rank.keys():
        i = rank[k].index(anycast_targets[k])
        rank_r[i] += 1
        i = rank[k].index(sid_targets[k])
        if i != 0:
            print(f'target: {sid_targets[k]}, ranks: {rank[k]}')
        rank_s[i] += 1
    print(f'rank_r = {rank_r}')
    print(f'rank_s = {rank_s}')
    anycast_additional_latency = {k: (latencies[k][anycast_targets[k]] -
                                      np.min(list(latencies[k].values()))) / 1
                                  for k in latencies.keys()}
    # print(anycast_additional_latency)
    print(f'Anycast additional latency: {np.mean(list(anycast_additional_latency.values()))}')
    statics = np.median
    statics2 = np.mean
    client_ips = []
    for client_region in CLIENT_REGIONS:
        for client_ip, value in data.items():
            if value['client_region'] == client_region:
                client_ips.append(client_ip)
                break
    sid_hs_list = []
    sid_tf_list = []
    dns_query_list = []
    dns_hs_list = []
    dns_tf_list = []
    any_hs_list = []
    any_tf_list = []
    routing_list = []
    x = np.array(range(len(client_ips)))
    for client_ip in client_ips:
        records = data[client_ip]['records']
        routing_list.append(
            [(data[client_ip]['client_region'], shorten(r['router_region']), r['server_region']) for r in records][0])
        sid_hs_list.append(statics([r['sid_hs'] for r in records]) / 1000)
        sid_tf_list.append(statics([r['sid_tf'] for r in records]) / 1000)
        dns_query_list.append(statics2([r['dns_query'] for r in records]))
        dns_hs_list.append(statics([r['dns_hs'] for r in records]) / 1000)
        dns_tf_list.append(statics([r['dns_tf'] for r in records]) / 1000)
        any_hs_list.append(statics([r['any_hs'] for r in records]) / 1000)
        any_tf_list.append(statics([r['any_tf'] for r in records]) / 1000)
    sid_hs_list = np.array(sid_hs_list)
    sid_tf_list = np.array(sid_tf_list)
    dns_query_list = np.array(dns_query_list)
    dns_hs_list = np.array(dns_hs_list)
    dns_tf_list = np.array(dns_tf_list)
    any_hs_list = np.array(any_hs_list)
    any_tf_list = np.array(any_tf_list)

    dns_hs_list0 = dns_hs_list.copy()
    dns_tf_list0 = dns_tf_list.copy()
    dns_hs_list += dns_query_list
    dns_tf_list += dns_query_list
    # print(routing_list)
    optimal_flags = np.array([x[1] == x[2] for x in routing_list])
    opt_idx = np.where(optimal_flags)[0]
    subopt_idx = np.where(optimal_flags == False)[0]
    optimal_ratio = len(list(filter(lambda x: x, optimal_flags))) / len(routing_list) * 100
    print(f'Anycast optimal ratio: {optimal_ratio}%')
    anycast_additional_hs = (any_hs_list[subopt_idx] - dns_hs_list0[subopt_idx]) / dns_hs_list0[subopt_idx] * 100
    anycast_additional_tf = (any_tf_list[subopt_idx] - dns_tf_list0[subopt_idx]) / dns_tf_list0[subopt_idx] * 100
    # print(f'Anycast additional handshake latency: {np.mean(anycast_additional_hs)}%')
    # print(f'Anycast additional transport latency: {np.mean(anycast_additional_tf)}%')
    print(f'Artemis handshake latency: {np.mean(sid_hs_list)}')
    print(f'Artemis transport latency: {np.mean(sid_tf_list)}')
    # print(f'DNS handshake latency: {np.mean(dns_hs_list)}')
    # print(f'DNS transport latency: {np.mean(dns_tf_list)}')
    # print(f'Anycast handshake latency: {np.mean(any_hs_list)}')
    # print(f'Anycast transport latency: {np.mean(any_tf_list)}')

    # fig, ax = plt.subplots(figsize=(8, 3))
    # width = 0.25
    # ax.bar(x - width, sid_tf_list, width, label='hestia', color='#f2cfa3')
    # ax.bar(x - width, sid_hs_list, width,
    #        label='hestia', color='#f2cfa3', hatch='////', edgecolor='#a27f53', linewidth=.8)
    # ax.bar(x, dns_tf_list, width, label='dns', color='#e75d56')
    # ax.bar(x, dns_hs_list, width,
    #        label='dns', color='#e75d56', hatch='////', edgecolor='#970906', linewidth=.8)
    # ax.bar(x, dns_query_list, width, label='dns', color='#bc5090')
    # ax.bar(x + width, any_tf_list, width, label='anycast', color='#aee1f4')
    # ax.bar(x + width, any_hs_list, width,
    #        label='anycast', color='#aee1f4', hatch='////', edgecolor='#5e91a4', linewidth=.8)
    # ax.tick_params(axis='both', which='major', labelsize=font_size - 2)
    # plt.gca().set_ylim(bottom=0)
    # plt.xticks(range(len(client_ips)), range(1, len(client_ips) + 1))
    # plt.xlabel('aws clients', fontsize=font_size)
    # plt.ylabel('latency (ms)', fontsize=font_size)
    # plt.ylim(0, 250)
    # if last:
    #     ax.legend(fontsize=font_size - 6, handles=[mpatches.patch(color='#f2cfa3', label='hestia'),
    #                                                mpatches.patch(color='#e75d56', label='dns'),
    #                                                mpatches.patch(color='#aee1f4', label='anycast'),
    #                                                mpatches.patch(color='#bc5090', label='dns query latency'),
    #                                                mpatches.patch(facecolor='#ffffff', label='transport latency',
    #                                                               edgecolor='#888888'),
    #                                                mpatches.patch(facecolor='#ffffff', label='handshake latency',
    #                                                               hatch='////', edgecolor='#888888'),
    #                                                ])
    # fig.tight_layout()
    # plt.savefig(os.path.join(data_path, f'{name}.pdf'),
    #             format='pdf', dpi=1000, bbox_inches='tight')
    # plt.show()


def main():
    init()
    files = (('res1/mysql.dump', '0 h'), ('res2/mysql.dump', '1 h'), ('res3/mysql.dump', '2 h'),
             ('res4/mysql.dump', '3 h'))
    files = (('res5/mysql.dump', '9 h'), )
    files = (('res6/mysql.dump', '18 h'), )
    for file_name, name in files:
        os.system(f'mysql -pjohnson -ujohnson serviceid_db < {os.path.join(DATA_PATH, file_name)}')
        handle_region(name)


if __name__ == '__main__':
    main()
