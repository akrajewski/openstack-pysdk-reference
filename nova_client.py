#!/usr/bin/env python

import os
import novaclient.client

class NovaClient(object):
    def __init__(self):
        credentials = self._get_credentials()
        self._nc = novaclient.client.Client(**credentials)

    def _get_credentials(self):
        d = {}
        d['version'] = '2'
        d['username'] = os.environ['OS_USERNAME']
        d['api_key'] = os.environ['OS_PASSWORD']
        d['auth_url'] = os.environ['OS_AUTH_URL']
        d['project_id'] = os.environ['OS_TENANT_NAME']
        return d

    def list_servers(self):
        servers = self._nc.servers.list()
        for server in servers:
            self._print_server(server)

    @staticmethod
    def _print_server(server):
        print("-"*35)
        print("server id: %s" % server.id)
        print("server name: %s" % server.name)
        print("server image: %s" % server.image)
        print("server flavor: %s" % server.flavor)
        print("server key name: %s" % server.key_name)
        print("user_id: %s" % server.user_id)
        print("-"*35, end="\n\n")


def main():
    client = NovaClient()
    client.list_servers()

if __name__ == '__main__':
    main()