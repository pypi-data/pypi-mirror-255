from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn

from .proxmox import ProxmoxMissingPermissionError, ProxmoxVMNotFoundError
from .util.exceptions import PVECLIError

guest_cli = typer.Typer()


@guest_cli.callback()
def guest(
        ctx: typer.Context,
        vm: Annotated[str, typer.Argument(help='VM Name or ID')]
):
    proxmox_api = ctx.obj['proxmox_api']

    try:
        proxmox_api.check_permission('/vms', 'VM.Audit')
    except ProxmoxMissingPermissionError as exc:
        raise PVECLIError(f'Missing permission for VM-Management ({exc.path}): {exc.permission}') from None

    try:
        vm_obj = proxmox_api.get_vm_by_id(int(vm)) if vm.isdigit() else proxmox_api.get_vm_by_name(vm)
    except ProxmoxVMNotFoundError:
        raise PVECLIError(f'VM {vm} was not found.') from None

    try:
        proxmox_api.check_permission(f'/vms/{vm_obj["vmid"]}', 'VM.Monitor')
    except ProxmoxMissingPermissionError as exc:
        raise PVECLIError(f'Missing permission for VM {vm_obj["name"]} ({exc.path}): {exc.permission}') from None

    ctx.obj['vm'] = vm_obj


@guest_cli.command()
def start(
        ctx: typer.Context,
        command: Annotated[list[str], typer.Argument()]
):
    """Start command on guest"""
    proxmox_api = ctx.obj['proxmox_api']
    vm = ctx.obj['vm']
    command_string = ' '.join(command)

    rprint(f'[blue]Starting {command_string} on {vm["name"]} ({vm["vmid"]})')
    pid = proxmox_api.execute(node=vm['node'], vm_id=vm['vmid'], command=command_string)
    rprint(f'[blue]PID: [green]{pid}')


@guest_cli.command()
def run(
        ctx: typer.Context,
        command: Annotated[list[str], typer.Argument()]
):
    """Execute command on guest and return output.

    Exits with the exitcode of the command inside the VM."""
    proxmox_api = ctx.obj['proxmox_api']
    vm = ctx.obj['vm']
    command_string = ' '.join(command)

    rprint(f'[blue]Running {command_string} on {vm["name"]} ({vm["vmid"]})')
    pid = proxmox_api.execute(node=vm['node'], vm_id=vm['vmid'], command=command_string)
    result = proxmox_api.check_exec_status(node=vm['node'], vm_id=vm['vmid'], pid=pid)
    if result['out_data']:
        rprint(result['out_data'])
    raise typer.Exit(code=result['exitcode'])


@guest_cli.command()
def upload(
        ctx: typer.Context,
        source: Annotated[Path, typer.Argument(help='Path of the source file. Use "-" to read from stdin.',
                                               exists=True, dir_okay=False, resolve_path=True, allow_dash=True)],
        destination: Annotated[Path, typer.Argument(help='Path of the destination file inside the guest.',
                                                    exists=False, readable=False)]
):
    """Upload file to guest"""
    proxmox_api = ctx.obj['proxmox_api']
    vm = ctx.obj['vm']

    with typer.open_file(str(source), mode='rb') as source_stream:
        source_file = source_stream.read()

    with Progress(SpinnerColumn(style='bold white', finished_text='[blue bold]⠿'),
                  TextColumn('[progress.description]{task.description}')) as progress:
        task_id = progress.add_task(description=f'[white]📤 Uploading {source} to {destination} '
                                                f'on {vm["name"]} ({vm["vmid"]})...',
                                    total=1)
        proxmox_api.file_write(node=vm['node'], vm_id=vm['vmid'], file_path=destination, content=source_file)
        progress.update(task_id, completed=1, refresh=True,
                        description=f'[blue]✅ Uploaded {source} to {destination} on {vm["name"]} ({vm["vmid"]})')
