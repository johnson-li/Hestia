import sqlite3

import boto3

from hestia import RESOURCE_PATH
from hestia.aws.regions import REGIONS

DB_PATH = RESOURCE_PATH + '/db'
DB_FILE = DB_PATH + '/instances.db'


def clear_cdn():
    client = boto3.client('route53')
    sets = client.list_resource_record_sets(HostedZoneId="Z2JGUQXL1NZ1A2")['ResourceRecordSets']
    sets = list(filter(lambda a: a['Type'] == 'A' and a['Name'].endswith('.xuebing.name.'), sets))
    client.change_resource_record_sets(HostedZoneId="Z2JGUQXL1NZ1A2", ChangeBatch={
        'Changes': [{'Action': 'DELETE', "ResourceRecordSet": se} for se in sets]})


def add_cdn():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    sets = []
    c.execute("SELECT * FROM instances")
    for host in c.fetchall():
        host = dict(zip([d[0] for d in c.description], host))
        if host['name'] == 'router':
            record = {'Name': 'sid.xuebing.name.', 'Type': 'A', 'SetIdentifier': REGIONS[host['region']],
                      'Region': host['region'], 'TTL': 60, 'ResourceRecords': [{'Value': host['secondaryIpv4Pub']}]}
            sets.append(record)
        elif host['name'] == 'server':
            record = {'Name': 'cdn.xuebing.name.', 'Type': 'A', 'SetIdentifier': REGIONS[host['region']],
                      'Region': host['region'], 'TTL': 60, 'ResourceRecords': [{'Value': host['primaryIpv4Pub']}]}
            sets.append(record)
            for i in range(50):
                record = {'Name': 'cdn{}.xuebing.name.'.format(i), 'Type': 'A',
                          'SetIdentifier': REGIONS[host['region']],
                          'Region': host['region'], 'TTL': 60, 'ResourceRecords': [{'Value': host['primaryIpv4Pub']}]}
                sets.append(record)
    client = boto3.client('route53')
    client.change_resource_record_sets(HostedZoneId="Z2JGUQXL1NZ1A2", ChangeBatch={
        'Changes': [{'Action': 'UPSERT', "ResourceRecordSet": se} for se in sets]})


def main():
    clear_cdn()
    add_cdn()


if __name__ == '__main__':
    main()
