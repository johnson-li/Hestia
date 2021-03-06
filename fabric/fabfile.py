import os
import sqlite3

from fabric.api import *
from fabric.io import CommandTimeout

from hestia.aws.regions import REGIONS
from hestia.gce.zones import ZONES, shrink

AWS = 'AWS' not in env or env.AWS != 'False'
DB_FILE = os.path.dirname(os.path.dirname(__file__)) + '/resources/db/%sinstances.db' % ('' if AWS else 'gcp_')

env.warn_only = True
env.skip_bad_hosts = True
env.use_ssh_config = True
env.ssh_config_path = os.path.dirname(os.path.dirname(__file__)) + '/resources/ssh/config'

if not env.hosts:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT region FROM instances GROUP BY region")
    env.hosts = []
    for region in c.fetchall():
        region = region[0]
        env.hosts.append((REGIONS[region].lower() if AWS else region) + '-router')
        env.hosts.append((REGIONS[region].lower() if AWS else region) + '-server')
    print('hosts: ' + str(env.hosts))
    conn.close()


@parallel(pool_size=8)
def host_type():
    run('uname -a')


@parallel(pool_size=8)
def add_rsa():
    run(
        'echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDBG6FkxAtokRbDWX3V0L4zYbfn0g6GvmJIQGdhbTc7eHk5QSMcCluQ2J9q8u9DYwrweGW7tNIX6vb8GCP85GHafHGnDe1wufVTIznB69cm0CkUsRlHOFVGuk1CCeiVYuZbPAbu3UPE/Q5QNRzKzeUKMzA4QHLF99kyFYruVDj29/3EPLIHSf/svGB27hT9jiOUzvTsoCanpYb3YbEv4qff87p6hslxyo2DvOydMjybPsGD0mOB+B2mtaA6FCAF89T0AokENUZK7pr/w31qz68avZT2yiWCFUEHKiu4GaAiUb8Z18Qp++VV17W3o81AdKxPgpXc+Wcrog9XX8oxePuz johnsonli1993@ubuntu-xenial-1" >> ~/.ssh/authorized_keys')


@parallel(pool_size=8)
def disable_ohmyzsh_update():
    run("sed -i -e '1iDISABLE_AUTO_UPDATE=true\\' .zshrc")


@parallel(pool_size=8)
def disable_ssh_dns_resolve():
    sudo('bash -c "echo \'UseDNS no\' >> /etc/ssh/sshd_config"')
    sudo('/etc/init.d/ssh restart')


@parallel(pool_size=8)
def hosts_file():
    sudo('bash -c "echo 127.0.0.1 `hostname` >> /etc/hosts"')


@parallel(pool_size=8)
def show_dpid():
    sudo('ovs-ofctl show br1| grep dpid')


@parallel(pool_size=8)
def show_mac():
    sudo('ifconfig br1| grep HWaddr')
    sudo('ifconfig eth1| grep HWaddr')


@parallel(pool_size=8)
def trace_route():
    sudo('apt update')
    sudo('apt install -y traceroute')
    sudo('traceroute -nw 1 -q 10 205.251.192.202')


@parallel(pool_size=8)
def ping_mesh():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT primaryIpv6 FROM instances")
    # c.execute("SELECT primaryIpv4Pub FROM instances where name = 'router'")
    for host in c.fetchall():
        run("echo '" + host[0] + "' `ping6 -c10 " + host[0] + "|tail -1|awk '{print $4}' | cut -d '/' -f 2`")


@parallel(pool_size=4)
def start_servers():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("select * from instances where primaryIpv4Pub = '{}'".format(env.host))
    self_host = dict(zip([d[0] for d in c.description], c.fetchone()))
    if self_host['name'] == 'server':
        run('tmux ls || tmux new-session -d -s server')
        run('tmux send-keys -t server:0 "sudo /home/%s/Workspace/server/serviceid_server" ENTER' % (
            'ubuntu' if AWS else 'johnsonli1993'))


@parallel(pool_size=4)
def stop_servers():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("select * from instances where primaryIpv4Pub = '{}'".format(env.host))
    self_host = dict(zip([d[0] for d in c.description], c.fetchone()))
    if self_host['name'] == 'server':
        sudo('killall serviceid_server')


@parallel(pool_size=8)
def init_nic():
    sudo('echo "auto lo\niface lo inet loopback\n\nauto eth0\niface eth0 inet dhcp\n\nauto eth1\n'
         'iface eth1 inet dhcp\n" > /etc/network/interfaces.d/50-cloud-init.cfg')
    sudo('echo "iface eth0 inet6 dhcp\niface eth0 inet6 dhcp\n" > /etc/network/interfaces.d/60-default-with-ipv6.cfg')
    sudo('/etc/init.d/networking restart', timeout=15)


@parallel(pool_size=8)
def init_ovs():
    sudo('/usr/local/share/openvswitch/scripts/ovs-ctl start')
    sudo('ovs-vsctl --may-exist add-br br1')
    sudo('ovs-vsctl --may-exist add-port br1 %s' % ('eth1' if AWS else 'ens5'))
    sudo('ovs-vsctl set-controller br1 tcp:35.193.107.149:6653')


@parallel(pool_size=8)
def show_neigh():
    run("ip neigh|grep eth1|egrep -o '([0-9a-f]{2}:){5}[0-9a-f]+'|head -n1 > ~/neigh.mac")
    run("echo 'neigh:' `cat ~/neigh.mac`")


@parallel(pool_size=8)
def clear_ovs():
    sudo('/usr/local/share/openvswitch/scripts/ovs-ctl stop')


@parallel(pool_size=4)
def clear_gre():
    sudo("for port in `sudo ovs-vsctl show|egrep 'vxlan|gre' -B2|grep Port| egrep 'Port (.+)'| sed -E 's/ +Port //'`; "
         "do sudo ovs-vsctl del-port br1 $port; done")


@parallel(pool_size=4)
def clear_flows():
    sudo("ovs-ofctl del-flows br1")


@parallel(pool_size=4)
def show_ovs():
    sudo("ovs-vsctl show")


# This are some bugs for gre in AWS Ohio, so we use vxlan now
@parallel(pool_size=4)
def setup_gre():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("select * from instances where primaryIpv4Pub = '{}'".format(env.host))
    self_host = dict(zip([d[0] for d in c.description], c.fetchone()))
    if self_host['name'] == 'server':
        # connect to the router
        c.execute("select * from instances where region = '{}' and name = '{}'".format(self_host['region'], 'router'))
        router_host = dict(zip([d[0] for d in c.description], c.fetchone()))
        sudo('ovs-vsctl add-port br1 gre_router -- set interface gre_router type=vxlan, options:remote_ip={}'.format(
            router_host['primaryIpv4']))
        sudo('ifconfig br1 10.10.10.10/24 up')
        sudo('ip route add default dev br1 tab 2')
        sudo('ip rule add from 10.10.10.10/24 tab 2 priority 600')
    elif self_host['name'] == 'router':
        # connect to the server
        c.execute("select * from instances where region = '{}' and name = '{}'".format(self_host['region'], 'server'))
        server_host = dict(zip([d[0] for d in c.description], c.fetchone()))
        sudo('ovs-vsctl add-port br1 gre_server -- set interface gre_server type=vxlan, options:remote_ip={}'.format(
            server_host['primaryIpv4']))
        commands = []
        for region in (REGIONS if AWS else ZONES):
            if region == self_host['region']:
                continue
            region_name = REGIONS[region].lower() if AWS else region
            # connect to other routers
            if region_name + '-router' in env.hosts:
                c.execute("SELECT * FROM instances WHERE region = '{}' and name = '{}'".format(region, 'router'))
                record = dict(zip([d[0] for d in c.description], c.fetchone()))
                remote_ip = record['primaryIpv4Pub']
                commands.append('add-port br1 {} -- set interface {} type=vxlan, options:remote_ip={}'.format(
                    shrink(region_name), shrink(region_name), remote_ip))
        sudo('ovs-vsctl ' + ' -- '.join(commands))


@parallel(pool_size=4)
def setup_bridge():
    result = run('ifconfig eth1| grep "inet addr"')
    add_eth1 = result.return_code != 0
    if add_eth1:
        sudo('bash -c "echo \'auto eth1\niface eth1 inet dhcp\niface eth1 inet6 dhcp\' >>'
             ' /etc/network/interfaces.d/50-cloud-init.cfg"')
        try:
            sudo('/etc/init.d/networking restart', timeout=5)
        except CommandTimeout as e:
            print(e)
    sudo('/usr/local/share/openvswitch/scripts/ovs-ctl start')
    sudo('sysctl -w net.ipv4.ip_forward=1')
    # sudo('ovs-vsctl del-br br1')
    sudo('ovs-vsctl add-br br1')
    sudo('ovs-vsctl add-port br1 eth1')
    sudo('ifconfig br1')
    sudo('ovs-ofctl show br1| grep dpid')
    # ipv4_0 = run("ifconfig eth0|grep 'inet addr'| gawk 'match($0, /inet addr:(.*?)  Bcast/, ary) {print ary[1]}'")
    # ipv4_1 = run("ifconfig eth1|grep 'inet addr'| gawk 'match($0, /inet addr:(.*?)  Bcast/, ary) {print ary[1]}'")
    # ipv6 = run("ifconfig eth1|grep 'Global'| gawk 'match($0, /inet6 addr: (.*?) Scope/, ary) {print ary[1]}'")
    # mac_eth = run("ifconfig eth1|grep 'HWaddr'| gawk 'match($0, /HWaddr (.*?)  /, ary) {print ary[1]}'")
    # mac_br = run("ifconfig br1|grep 'HWaddr'| gawk 'match($0, /HWaddr (.*?)  /, ary) {print ary[1]}'")
    # gateway = run("route -n| gawk 'match($0, /0\.0\.0\.0 +([0-9.]+).*eth0/, ary) {print ary[1]}'| head -n1")
    # sudo('ifconfig br1 {}/20 up'.format(ipv4_1))
    # sudo('ifconfig br1 inet6 add {}'.format(ipv6))
    # sudo('ovs-vsctl add-port br1 eth1')
    # sudo('ovs-ofctl add-flow br1 priority=100,in_port=eth1,actions=mod_dl_dst:{},local'.format(mac_br))
    # sudo('ovs-ofctl add-flow br1 priority=100,in_port=local,actions=mod_dl_src:{},eth1'.format(mac_eth))
    # sudo('ifconfig eth1 0')
    # sudo('ip route add default via {} dev eth0 tab 1'.format(gateway))
    # sudo('ip route add default via {} dev eth1 tab 2'.format(gateway))
    # sudo('ip rule add from {}/24 tab 1 priority 500'.format(ipv4_0))
    # sudo('ip rule add from {}/24 tab 2 priority 600'.format(ipv4_1))
