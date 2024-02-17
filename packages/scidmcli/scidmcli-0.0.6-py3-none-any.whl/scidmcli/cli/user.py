import click
from scidmcli.credential import Credential
from scidmcli.connection import connect_to_ckan


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS, help='Manage user [list|token]')
def cli():
    pass

@click.command(help='list the organizations or datasets that the user has permission')
@click.option('-t', '--type', help='the type of organizations or datasets', 
              required=True, type=click.Choice(['ds', 'org']))
@click.option('-d', '--detail', help='the detail of organizations or datasets', is_flag=True)
def list(type, detail):
    with connect_to_ckan() as ckan:
        if type == 'ds':
            r = ckan.action.package_search()
            if detail:
                filtered_list = [key for key in r['results'] if key.get('usable') == True]
                click.echo(filtered_list)
            else:
                filtered_list = [key['title'] for key in r['results'] if key.get('usable') == True]
                click.echo(filtered_list)
        elif type == 'org':
            r = ckan.action.organization_list_for_user()
            if detail:
                click.echo(r)
            else:
                filtered_list = [key['title'] for key in r]
                click.echo(filtered_list)
        else:
            raise ValueError('Invalid type.')

@click.command(help='show user\'s token')
def token():
    click.echo(Credential._getAPIConfig()[0])

cli.add_command(list)
cli.add_command(token)
