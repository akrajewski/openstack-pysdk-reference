#!/usr/bin/env python

import os
import time
import heatclient.client
import keystoneclient.v2_0.client
import logging
import heatclient.exc

from heatclient.common import template_utils
from urllib.parse import urlparse

logging.basicConfig(
    format='%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class HeatClient:

    HEAT_API_PORT = 8004

    def __init__(self):
        username = os.environ['OS_USERNAME']
        password = os.environ['OS_PASSWORD']

        auth_url = urlparse(os.environ['OS_AUTH_URL'])

        keystone_creds = {
            'username': username,
            'password': password,
            'tenant_name': os.environ['OS_TENANT_NAME'],
            'auth_url': auth_url.geturl()
        }

        keystone = keystoneclient.v2_0.client.Client(**keystone_creds)

        heat_creds = {
            'endpoint': self._heat_url(auth_url.hostname, keystone.tenant_id),
            'token': keystone.auth_token,
        }

        self._hc = heatclient.client.Client('1', **heat_creds)

    @classmethod
    def _heat_url(cls, hostname, tenant_id):
        return 'http://{0}:{1}/v1/{2}'.format(
            hostname,
            cls.HEAT_API_PORT,
            tenant_id)

    def get_stacks(self):
        return self._hc.stacks.list()

    def get_stack(self, stack_name):
        return self._hc.stacks.get(stack_name)

    def create_stack(self, stack_name, template_file, parameters):
        tpl_files, template = template_utils.get_template_contents(template_file)

        self.validate_template(template, tpl_files)
        
        # Comment this out and pass proper env_paths if you want to use envs
        # env_files, env = template_utils.process_multiple_environments_and_files(
        #    env_paths=None)
        
        fields = {
            'stack_name': stack_name,
            'disable_rollback': True,
            'parameters': parameters,
            'template': template,
            'files': dict(list(tpl_files.items())),
        }

        self._hc.stacks.create(**fields)

        return self._hc.stacks.get(stack_name)

    def delete_stack(self, stack_name):
        self._hc.delete_stack(stack_name)

    def validate_template(self, template, template_files):
        fields = {
            'template': template,
            'files': dict(list(template_files.items())),
        }

        # This will raise an exception if validation fails
        self._hc.stacks.validate(**fields)

    def get_resources(self, stack_name):
        return self._hc.resources.list(stack_name)


def main():
    log.info("Instantianting Heat client")
    client = HeatClient()

    # Name and initial parameters of stack to create
    stack_name = 'example'
    stack_params = {
        'image': 'cirros-0.3.2-x86_64-uec',
        'flavor':'m1.tiny'
    }
    stack_template_path = 'hot/example_instance.yaml'

    # Try to create stack
    # If error occurs e.g. stack already exists, an exception is thrown
    try:
        log.info("Creating stack %s", stack_name)
        client.create_stack(stack_name, stack_template_path, stack_params)
    except heatclient.exc.HTTPConflict as exc:
        log.error("Error while creating stack: %s", exc.message)

    # Get created stack
    example_stack = client.get_stack(stack_name)

    log.info('Waiting for stack to be created...')
    while example_stack.stack_status != 'CREATE_COMPLETE':
        log.debug('Stack status: ' + example_stack.stack_status)
        time.sleep(2)

        # Retrieve current stack info
        # ** WARNING ** This does not retrieve outputs and other final data
        example_stack.get()

    log.info('Stack created successfully')

    # Fetch again to populate all the output values
    example_stack = client.get_stack(example_stack.stack_name)

    log.info("Listing outputs. One per line")
    for output in example_stack.outputs:
        log.info("Output: %s", output)

    log.info("Listing resources of the created stack. One per line.")
    for resource in client.get_resources(stack_name):
        log.info("Resource: %s", resource)

    log.info("Everything good. Deleting stack")
    example_stack.delete()

if __name__ == '__main__':
    main()
