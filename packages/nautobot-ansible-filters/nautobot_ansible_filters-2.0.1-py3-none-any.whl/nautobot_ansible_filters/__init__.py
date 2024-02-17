"""Plugin declaration for ansible_filters."""
# Metadata is inherited from Nautobot. If not including Nautobot in the environment, this should be added
try:
    from importlib import metadata
except ImportError:
    # Python version < 3.8
    import importlib_metadata as metadata

__version__ = metadata.version(__name__)

from nautobot.extras.plugins import PluginConfig


class AnsibleFiltersConfig(PluginConfig):
    """Plugin configuration for the ansible_filters plugin."""

    name = "nautobot_ansible_filters"
    verbose_name = "Nautobot Ansible Filters"
    version = __version__
    author = "Mikhail Yohman"
    description = "Nautobot plugin to include Ansible built-in Jinja filters."
    base_url = "ansible-filters"
    required_settings = []
    min_version = "1.2.0"
    max_version = "2.9999"
    default_settings = {}
    caching_config = {}


config = AnsibleFiltersConfig  # pylint:disable=invalid-name
