"""Unit tests for ansible_filters."""
from django.apps import apps
from django.test import TestCase

from django_jinja import library
from nautobot_ansible_filters.utilities import gather_filter_plugins


class AppConfigReadyTest(TestCase):
    """Test the AnsibleFilters API."""

    def setUp(self):
        """Initiate the app config for all tests."""
        self.app_config = apps.get_app_config("nautobot_ansible_filters")
        self.found_filters = set(gather_filter_plugins())

    def test_app_config_ready_templates_exist(self):
        """Verify ALL ansible-core filters are loaded properly within app_config.ready()."""
        # self.app_config.ready()
        django_filters = {
            filter
            for filter in library._local_env["filters"]  # pylint: disable=protected-access
            if "ansible" in filter
        }
        self.assertEqual(
            self.found_filters,
            django_filters,
        )
