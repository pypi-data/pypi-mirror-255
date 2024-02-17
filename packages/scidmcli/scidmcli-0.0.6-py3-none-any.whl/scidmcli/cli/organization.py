import click
from scidmcli.connection import connect_to_ckan


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS, help='Manage organization [list]')
def cli():
    pass

@click.command(help='show organization')
@click.option('-d', '--detail', help='the detail of organizations', is_flag=True)
def list(detail):
    with connect_to_ckan() as ckan:
        r = ckan.action.organization_list(all_fields=detail)
        click.echo(r)

cli.add_command(list)