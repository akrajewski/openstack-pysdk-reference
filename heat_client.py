#!/usr/bin/env python

import os
import heatclient.client
import keystoneclient.v2_0.client

from heatclient.common import template_utils

class HeatClient:

    def __init__(self):

        username = os.environ['OS_USERNAME']
        password = os.environ['OS_PASSWORD']

        keystone_creds = {
            'username': username,
            'password': password,
            'tenant_name': os.environ['OS_TENANT_NAME'],
            'auth_url': os.environ['OS_AUTH_URL']
        }

        keystone = keystoneclient.v2_0.client.Client(**keystone_creds)

        auth_token = keystone.auth_token
        
        heat_creds= {
            'endpoint': 'http://128.142.186.204:8004/v1/5da96715e3574782b75b4e9ec8a0ca41',
            'token': auth_token,
        }

        
        self._hc = heatclient.client.Client('1', **heat_creds)

    def list_stacks(self):
        stacks = self._hc.stacks.list()

        for stack in stacks:
            print(stack, end="\n\n")


    def create_stack(self, name, template_file):
        tpl_files, template = template_utils.get_template_contents(template_file)
        
        env_files, env = template_utils.process_multiple_environments_and_files(env_paths=None)

        fields = {
            'stack_name': name,
            'disable_rollback': True,
            # 'parameters': utils.format_parameters(args.parameters),
            'template': template,
            'files': dict(list(tpl_files.items()) + list(env_files.items())),
            'environment': env
        }

        print(fields)


        # hc.stacks.create(**fields)
        # do_stack_list(hc)



def main():
    client = HeatClient()

    # List all stacks
    client.list_stacks()

    

if __name__ == '__main__':
    main()
        