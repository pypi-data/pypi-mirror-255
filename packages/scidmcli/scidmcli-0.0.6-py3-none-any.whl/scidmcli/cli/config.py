import click
from scidmcli.util import isNone, validate
from scidmcli.credential import Credential


# Set credential function
def setCredential(apikey=None, msg=None):
    if isNone(apikey) or len(apikey) == 0:
        apikey = click.prompt('Please enter API key', type=str)

    if validate(apikey):
        Credential(scidm_api_key=apikey)
        click.echo(msg)
        print(Credential())
    else:
        click.echo('Invalid API key format.')
    
# Context settings for CLI    
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help']) 

@click.group(context_settings=CONTEXT_SETTINGS, help='Configure the SCIDM CLI [info|init|reset]')
def cli():
    pass

@click.command(help='Get exsisting information.')
def info():
    if Credential._isValidCredential():
        info = Credential()
        click.echo('Hi, your information:')
        print(info)
    else:
        click.echo('Please set credential first.')

@click.command(help='Initialize the credential.')
@click.option('-a', '--apikey', help='API key for CLI.')
def init(apikey):
    if not Credential._isValidCredential():
        setCredential(apikey=apikey, msg='Hi, Welcome!')
    else:
        click.echo('Credential Existed.')

@click.command(help='Reset the credential.')
@click.option('-a', '--apikey', help='API key for CLI.')  
def reset(apikey):
    if Credential._isValidCredential():
        setCredential(apikey=apikey, msg='Your credential has been reset')
    else:
        click.echo('Please set credential first.')

cli.add_command(info)
cli.add_command(init)
cli.add_command(reset)
