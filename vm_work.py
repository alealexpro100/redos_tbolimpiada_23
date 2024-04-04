import os
import subprocess
import libvirt
from jinja2 import Environment, FileSystemLoader
import uuid
import tempfile
from pathlib import Path
import time

import paramiko

SNAPSHOT_XML_TEMPLATE = """<domainsnapshot>
  <name>{name}</name>
  <description>{description}</description>
</domainsnapshot>"""

CHECKER_NAME = "checker"
CHECKER_PASSWORD = "MyPassword123"

DEFAULT_USER_DATA= f"""users:
  - name: {CHECKER_NAME}
    groups: sudo
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    plain_text_passwd: '{CHECKER_PASSWORD}'
    lock_passwd: false
    shell: /bin/bash
"""

USERS_USER= """  - name: {USERNAME}
    groups: sudo
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    plain_text_passwd: '{PASSWORD}'
    lock_passwd: false
    shell: /bin/bash
"""

class qemu_vm():
    def __init__(self, machine_name: str="project-vm", network_name: str="net-test"):
        self.domain_name=machine_name
        self.network_name = network_name
        self.conn = libvirt.open("qemu:///system")
        self.ip_addr= None
        self.ssh = None
        env = Environment(loader=FileSystemLoader('templates'))
        try:
            self.dom = self.conn.networkLookupByName(self.network_name)
        except libvirt.libvirtError as e:
            template = env.get_template('network.xml')
            xmlconfig = template.render(
                name = self.network_name,
                uuid = uuid.uuid4()
            )
            self.conn.networkCreateXML(xmlconfig)
            print(f"No network found. Creating new one \"{self.network_name}\".")
        try:
            self.dom = self.conn.lookupByName(self.domain_name)
        except libvirt.libvirtError as e:
            print(f"No machine found. Creating new one \"{self.domain_name}\".")
            template = env.get_template('vm.xml')
            xmlconfig = template.render(
                name = self.domain_name,
                uuid = uuid.uuid4(),
                network_name = self.network_name
            )
            self.dom = self.conn.defineXMLFlags(xmlconfig, 0)
            self.dom.snapshotCreateXML(SNAPSHOT_XML_TEMPLATE.format(name='clean', description="Cloud-init"))
    def __del__(self):
        return self.conn.close()
    def power_on(self):
        return self.dom.create()
    def power_off(self):
        self.ip_addr = None
        return self.dom.shutdown()
    def gen_ci(self, user_data: str=DEFAULT_USER_DATA) -> None:
        iso_name = Path(os.getcwd()) / 'images' / 'ci.iso'
        with tempfile.TemporaryDirectory() as tmpdirname:
            temp_dir = Path(tmpdirname)
            (temp_dir / "meta-data").write_text(f"instance-id: {self.domain_name}\nlocal-hostname: {self.domain_name}\n")
            (temp_dir / "user-data").write_text(f"#cloud-config\n\n{user_data}")
            subprocess.run(args=['rm', '-rf', iso_name], capture_output=True, check=True)
            cmd_args = f"genisoimage -output {iso_name} -volid cidata -joliet -rock {temp_dir / 'meta-data'} {temp_dir / 'user-data'}".split(' ')
            subprocess.run(args=cmd_args, capture_output=True, check=True)
    def snapshot_restore(self, snapshot_name: str="clean"):
        snapshot = None
        for x in self.dom.listAllSnapshots():
            if x.getName() == snapshot_name:
                snapshot = x
                break
        else:
            raise libvirt.libvirtError('Could not find any snapshots')
        return self.dom.revertToSnapshot(snapshot)
    def ip_get(self):
        if self.ip_addr:
            return self.ip_addr
        ifaces = self.dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0)
        for (name, val) in ifaces.items():
            if val['addrs'] and name != 'lo':
                for ipaddr in val['addrs']:
                    if ipaddr['type'] == libvirt.VIR_IP_ADDR_TYPE_IPV4 and ipaddr['addr'] != '127.0.0.1':
                        self.ip_addr = ipaddr['addr']
                        return ipaddr['addr']
        return None
    def ip_get_wait(self):
        ip_addr = None
        print("Trying to get IP address...")
        while True:
            try:
                ip_addr = self.ip_get()
                if ip_addr:
                    break
            except libvirt.libvirtError as e:
                if str(e)=='Агент гостя не отвечает: Агент гостевой системы QEMU не подключён':
                    pass
                else:
                    raise e
            time.sleep(5)
        return ip_addr
    def do_paramiko_ssh(self, username: str, password: str, cmd: str):
        if not self.ssh:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        self.ssh.connect(self.ip_get_wait(), username=username, password=password)
        return self.ssh.exec_command(cmd)
    def port_forward(self, port_ext: int=432, port_int: int=22, remove: bool=False) -> str:
        cmd_args = ' '.join(['sudo', './port_forward.sh', ('remove' if remove else 'add'), 
                    str(port_ext), str(port_int), self.ip_get_wait()])
        print(f"Running \"{cmd_args}\"...")
        return subprocess.run(args=cmd_args, capture_output=True, check=True, shell=True)

if __name__ == "__main__":
    vm = qemu_vm()
    vm.gen_ci()
    vm.snapshot_restore()
    vm.power_on()
    vm.port_forward()
    vm.port_forward(remove=True)
