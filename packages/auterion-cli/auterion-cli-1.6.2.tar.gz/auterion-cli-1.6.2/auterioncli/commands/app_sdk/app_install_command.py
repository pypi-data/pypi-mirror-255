import os
import yaml
from datetime import datetime

from auterioncli.commands.command_base import CliCommand
from .update import do_update


def error(msg, code=1):
    print(msg)
    exit(code)


class AppInstallCommand(CliCommand):
    @staticmethod
    def help():
        return 'Install AuterionOS app to a connected device'

    def needs_device(self, args):
        return True

    def __init__(self, config):
        self._config = config
        self._device_address = config['device_address']

    def setup_parser(self, parser):
        parser.add_argument('artifact', help='Artifact to install on the device', nargs='?', default='.')

    def run(self, args):
        artifact = args.artifact

        if artifact == '.':
            # figure out artifact name from auterion-app.yml
            if not os.path.exists('auterion-app.yml'):
                error('Not an app directory. Run this command from the root of an app '
                      'directory or specify a .auterionos file to install. Exiting..')
            with open('auterion-app.yml') as f:
                try:
                    meta = yaml.safe_load(f)
                except yaml.YAMLError as e:
                    error(f'Failed to parse auterion-app.yml: {e}. Exiting..')
            if 'app-name' not in meta or 'app-author' not in meta:
                error('auterion-app.yml is missing app-name or app-author. Exiting..')

            slug = meta['app-author'] + '.' + meta['app-name']
            artifact_path = os.path.join('build', slug + '.auterionos')
            if not os.path.exists(artifact_path):
                error(f'No artifact found at {artifact_path}. Did you build? Exiting..')

            last_modified_date = datetime.fromtimestamp(os.path.getmtime(artifact_path))
            print(f'Artifact {artifact_path} last modified at {last_modified_date}')
            artifact = artifact_path

        if os.path.exists(artifact) and os.path.isfile(artifact):
            print(f'Installing artifact {artifact}')
            do_update(artifact, self._device_address, self._config['cookies'], self._config['extra_headers'])

        else:
            error(f'No upload artifact at {artifact}. Exiting..')
