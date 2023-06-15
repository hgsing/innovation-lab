from unittest import TestCase
from . import information_provider, state

# Create your tests here.
class DevicesTestCase(TestCase):
    cfg = None

    def setUp(self) -> None:
        self.cfg = state.config

    def test_devices_loaded(self):
        self.assertGreater(len(state.devices), 0)

    