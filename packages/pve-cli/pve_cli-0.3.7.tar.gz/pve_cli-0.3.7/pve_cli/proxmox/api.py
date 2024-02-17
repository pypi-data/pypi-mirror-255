import base64
import time
from operator import itemgetter
from pathlib import Path

from proxmoxer import ProxmoxAPI
from requests.exceptions import ConnectionError

from .exceptions import ProxmoxConnectionError, ProxmoxMissingPermissionError, ProxmoxNodeNotFoundError, ProxmoxVMNotFoundError
from .types import ExecStatus


class Proxmox:
    def __init__(self, host: str, user: str, realm: str, token_name: str, token_secret: str,
                 verify_ssl: bool | str = True, **kwargs: dict):
        self.api = ProxmoxAPI(
            host=host,
            user=f'{user}@{realm}',
            token_name=token_name,
            token_value=token_secret,
            verify_ssl=verify_ssl,
            **kwargs
        )

        try:
            self.api.version.get()
        except ConnectionError as exc:
            raise ProxmoxConnectionError(
                f'Could not connect to Proxmox API at {self.api._backend.get_base_url()}') from exc

    def get_task_status(self, node: str, upid: str) -> dict:
        status = self.api.nodes(node).tasks(upid).status.get()
        return dict(status)

    def check_permission(self, path: str, permission: str):
        permissions = self.api.access.permissions.get(path=path)[path]
        if permission not in permissions:
            raise ProxmoxMissingPermissionError(path, permission)

    def list_nodes(self) -> list:
        nodes = self.api.nodes.get()
        return sorted(nodes, key=itemgetter('node'))

    def get_node(self, node: str) -> dict:
        nodes = self.list_nodes()
        for node_dict in nodes:
            if node_dict['node'] == node:
                return dict(node_dict)
        raise ProxmoxNodeNotFoundError(f'Node {node} was not found.')

    def reboot_node(self, node: str):
        self.api.nodes(node).status.post(command='reboot')

    def list_vms(self) -> list:
        vms = self.api.cluster.resources.get(type='vm')
        return sorted(vms, key=itemgetter('vmid'))

    def get_vm_by_name(self, vm_name: str) -> dict:
        vm_list = self.api.cluster.resources.get(type='vm')
        vm = [vm for vm in vm_list if vm['name'] == vm_name]

        if len(vm) == 0:
            raise ProxmoxVMNotFoundError(vm_name)

        return dict(vm[0])

    def get_vm_by_id(self, vm_id: int) -> dict:
        vm_list = self.api.cluster.resources.get(type='vm')
        vm = [vm for vm in vm_list if vm['vmid'] == vm_id]

        if len(vm) == 0:
            raise ProxmoxVMNotFoundError(vm_id)

        return dict(vm[0])

    def migrate_vm(self, vm_id: int, target_node: str) -> tuple[str, str]:
        vm = self.get_vm_by_id(vm_id)
        upid = self.api.nodes(vm['node']).qemu(vm_id).migrate.post(target=target_node, online=1)
        return str(vm['node']), str(upid)

    def execute(self, node: str, vm_id: int, command: str) -> int:
        exec_res = self.api.nodes(node).qemu(vm_id).agent.exec.post(command=command)
        return int(exec_res['pid'])

    def check_exec_status(self, node: str, vm_id: int, pid: int, timeout: int = 120) -> ExecStatus:
        start = time.time()
        now = time.time()

        while now - start < timeout:
            exec_status = self.api.nodes(node).qemu(vm_id).agent('exec-status').get(pid=pid)
            if exec_status.get('exited', 0) == 1:
                return ExecStatus(exitcode=exec_status.get('exitcode'), out_data=exec_status.get('out-data'))

            time.sleep(1)
            continue

        raise TimeoutError(f'Could not get result of process {pid} on {vm_id} within {timeout} seconds.')

    def file_write(self, node: str, vm_id: int, file_path: Path, content: bytes):
        content_encoded = base64.b64encode(content)
        self.api.nodes(node).qemu(vm_id).agent('file-write').post(content=content_encoded, file=file_path, encode=0)
