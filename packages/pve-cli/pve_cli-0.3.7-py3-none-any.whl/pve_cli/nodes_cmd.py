import json
import time
from datetime import timedelta
from typing import Annotated

import typer
from rich import print as rprint
from rich.bar import Bar
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Column, Table

from .proxmox import Proxmox

nodes_cli = typer.Typer()

spinner_col = SpinnerColumn(style='bold white', finished_text='[blue bold]⠿')
text_col = TextColumn('[progress.description]{task.description}')


@nodes_cli.callback()
def nodes_callback(
        ctx: typer.Context
):
    proxmox_api = ctx.obj['proxmox_api']
    nodes = proxmox_api.list_nodes()
    ctx.obj['nodes'] = nodes


@nodes_cli.command('dump-vm-mapping')
def dump_vms(
        ctx: typer.Context,
        outfile: Annotated[typer.FileTextWrite, typer.Argument(help='JSON output filepath')],
):
    proxmox_api = ctx.obj['proxmox_api']
    vms = proxmox_api.list_vms()

    result = {vm['vmid']: vm['node'] for vm in vms}
    json.dump(result, outfile, indent=2)


@nodes_cli.command('restore-vm-mapping')
def restore_mapping(
        ctx: typer.Context,
        infile: Annotated[typer.FileText, typer.Argument(help='JSON input file (created with dump-vms')]
):
    proxmox_api = ctx.obj['proxmox_api']
    vms = proxmox_api.list_vms()
    nodes = ctx.obj['nodes']

    mapping = json.load(infile)

    migration_vms = {node['node']: [] for node in nodes}  # type: dict[str, list[dict]]
    for vm in vms:
        try:
            wanted_node = mapping[str(vm['vmid'])]
        except KeyError:
            continue

        if wanted_node == vm['node']:
            rprint(f'[green]✅ VM {vm["name"]} ({vm["vmid"]}) is on node {wanted_node}')
        else:
            migration_vms[wanted_node].append(vm)

    for dest_node, vms_to_migrate in migration_vms.items():
        if vms_to_migrate:
            migrate_vms(proxmox_api, dest_node, vms_to_migrate)


@nodes_cli.command('cluster-reboot')
def reboot_cluster(
        ctx: typer.Context
):
    proxmox_api = ctx.obj['proxmox_api']
    nodes = ctx.obj['nodes']
    vms = proxmox_api.list_vms()

    for i in range(len(nodes)):
        node = nodes[i]['node']
        tmp_node = nodes[i - 1]['node']

        node_running_vms = [vm for vm in vms if vm['status'] == 'running' and vm['node'] == node]

        migrate_vms(proxmox_api, tmp_node, node_running_vms)

        with Progress(spinner_col, TimeElapsedColumn(), text_col) as progress:
            task_id = progress.add_task(description=f'[white]Rebooting {node}...',
                                        total=1)
            proxmox_api.reboot_node(node)
            # wait for node to go offline
            while proxmox_api.get_node(node)['status'] == 'online':
                time.sleep(5)
            # wait for node to come online
            while proxmox_api.get_node(node)['status'] != 'online':
                time.sleep(5)
            progress.update(task_id, completed=1, refresh=True,
                            description=f'[blue]Done: Rebooted {node}')

        migrate_vms(proxmox_api, node, node_running_vms)


@nodes_cli.command('list')
def list_(
        ctx: typer.Context
):
    cluster = ctx.obj['cluster']
    nodes = ctx.obj['nodes']

    table = Table(title=f'Nodes in cluster {cluster}')
    table.add_column('Node')
    table.add_column('Status', justify='center')
    table.add_column('Cores', justify='right')
    table.add_column('CPU Usage')
    table.add_column('RAM')
    table.add_column('RAM Usage')
    table.add_column('Disk Usage')
    table.add_column('Uptime')

    for node in nodes:
        status = '🚀' if node['status'] == 'online' else '💀'
        ram = b2gb(node['maxmem'])
        cpu_bar = percentage_bar(node['cpu'])
        ram_bar = percentage_bar(node['mem'] / node['maxmem'])
        disk_bar = percentage_bar(node['disk'] / node['maxdisk'], 13)

        table.add_row(node['node'], status, str(node['maxcpu']), cpu_bar, f'{ram} GB', ram_bar,
                      disk_bar, str(timedelta(seconds=node['uptime'])))

    console = Console()
    console.print(table)


def b2gb(bytes_: int) -> int:
    return int(round(bytes_ / 1024 / 1024 / 1024, 0))


def percentage_bar(usage: float, max_width: int = 30) -> Table:
    percent = int(round(usage * 100, 0))
    field = Table.grid(Column(no_wrap=True, max_width=max_width - 5),
                       Column(no_wrap=True, min_width=5, justify='right'))
    field.add_row(Bar(size=1.0, begin=0.0, end=usage), f'{percent}%')
    return field


def migrate_vms(api: Proxmox, dest_node: str, vm_list: list):
    running_tasks = {}
    with Progress(spinner_col, text_col) as progress:
        for vm in vm_list:
            source_node, upid = api.migrate_vm(vm['vmid'], dest_node)
            task_id = progress.add_task(
                description=f'[white]🚚 Migrating {vm["name"]} ({vm["vmid"]}) from {source_node} to {dest_node}...',
                total=1)
            running_tasks[upid] = (vm, source_node, task_id)

        running_tasks_list = list(running_tasks)
        while running_tasks_list:
            for upid in running_tasks_list:
                vm, source_node, task_id = running_tasks[upid]
                status = api.get_task_status(source_node, upid)
                if status['status'] == 'stopped':
                    progress.update(task_id, completed=1, refresh=True,
                                    description=f'[blue]✅ Migrated {vm["name"]} ({vm["vmid"]}) '
                                                f'from {source_node} to {dest_node}')
                    running_tasks_list.remove(upid)
