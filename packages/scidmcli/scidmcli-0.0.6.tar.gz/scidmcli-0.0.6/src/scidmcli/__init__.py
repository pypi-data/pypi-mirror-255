import os
import yaml
import logging
import logging.config


# Check if SCIDM_CLI_PATH is set, if not default to user's home directory
if not ("SCIDM_CLI_PATH" in os.environ and os.path.isdir(os.environ['SCIDM_CLI_PATH'])):
    homepath = os.environ['HOME'] if 'HOME' in os.environ else os.environ['HOMEPATH']
    os.environ['SCIDM_CLI_PATH'] = os.path.join(os.path.expanduser("~"), homepath, ".scidm_cli")

# Create log directory if it doesn't exist    
def create_log_dir():
    log_dir = os.path.join(os.environ['SCIDM_CLI_PATH'], 'log')

    if not os.path.isdir(log_dir):
        os.mkdir(os.environ['SCIDM_CLI_PATH'])
        os.mkdir(log_dir)

    return log_dir

# Get log directory
log_dir = create_log_dir()

# Load logging config
PackageYaml = '{}/scidmcli/yaml/logging.yaml'.format(
        os.path.dirname(
            os.path.dirname(os.path.realpath(__file__))))
with open(PackageYaml, 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    
# Update log file path    
log_file_name = config['handlers']['file']['filename']
config['handlers']['file']['filename'] = os.path.join(
    log_dir, log_file_name)
    
# Configure logging
logging.config.dictConfig(config)
logger = logging.getLogger('command')

# Set environment variables
os.environ['LANG'] = 'C.UTF-8'
os.environ['LC_ALL'] = 'C.UTF-8'
