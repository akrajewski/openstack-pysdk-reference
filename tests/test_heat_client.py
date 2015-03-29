import pytest
import heat_client

class TestHeatClient:
    @classmethod
    def setup_class(self):
        self.hc = heat_client.HeatClient()

    def test_list_stacks(self):
        stacks = self.hc.list_stacks()
        print(stacks)