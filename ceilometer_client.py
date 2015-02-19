#!/usr/bin/env python

import os
import ceilometerclient.client 

class CeilometerClient:

    def __init__(self):
        args = ('username', 'password', 'tenant_id', 'tenant_name', 'auth_url')
        params = {value: os.environ['OS_{0}'.format(value.upper())] for value in args}
        self._cc = ceilometerclient.client.get_client(2, **params)

    def list_meters(self, query=None):
        meters = self._cc.meters.list(query)
        for meter in meters:
            print(meter, end="\n\n")

    def list_samples(self, meter_name=None, query=None, limit=None):
        samples = self._cc.samples.list(meter_name, query, limit)
        for sample in samples:
            print(sample, end="\n\n")


def main():
    client = CeilometerClient()
    
    # List all meters
    client.list_meters()

    # List cpu_util meter only
    query = [{
        'field': 'resource_id',
        'op': 'eq',
        'value': '<resource_id>'
    }]
    client.list_meters(query)

    # Get cpu_util samples
    client.list_samples(meter_name='cpu_util')

    # Get only latest sample
    client.list_samples(meter_name='cpu_util', limit=1)


if __name__ == '__main__':
    main()