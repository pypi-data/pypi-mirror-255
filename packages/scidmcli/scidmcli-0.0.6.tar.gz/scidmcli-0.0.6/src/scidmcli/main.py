import os
import click
from scidmcli.version import __version__ 
from scidmcli import logger


# Folder containing command modules 
plugin_folder = os.path.join(os.path.dirname(__file__), 'cli')


class SCIDMCLI(click.MultiCommand):

    # List available commands
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(plugin_folder):
            if filename.endswith('.py') and filename != '__init__.py':
                rv.append(filename[:-3])
        rv.sort()
        return rv

    # Import and return command module
    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(plugin_folder, name + '.py')
        try:
            with open(fn) as f:
                code = compile(f.read(), fn, 'exec')
                eval(code, ns, ns)

            return ns['cli']
        except FileNotFoundError as e:
            logger.exception(e)
    
    # Invoke command and handle exceptions
    def invoke(self, ctx):
        try:
            return super(SCIDMCLI, self).invoke(ctx)
        except click.exceptions.Exit:
            pass
        except click.exceptions.MissingParameter as e:
            click.echo(e.show()) 
        except Exception as e:
            click.echo(f'{type(e).__name__}: {e}')
            logger.exception(e)


# Print version number callback
def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'This version is {__version__}')
    ctx.exit()
    
# Create command context
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help']) 

# Main CLI entrypoint
@click.command(context_settings=CONTEXT_SETTINGS, cls=SCIDMCLI)
@click.option('-v', '--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True, help='Show scidm-cli version')
def cli():
    pass
