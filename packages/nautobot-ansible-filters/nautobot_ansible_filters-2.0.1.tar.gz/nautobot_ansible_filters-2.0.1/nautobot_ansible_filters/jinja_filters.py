"""Dynamically loading filter plugins/Jinja filters from ansible-core."""
from django_jinja import library
from nautobot_ansible_filters.utilities import gather_filter_plugins


for filter_name, filter_func in gather_filter_plugins().items():
    library.filter(name=filter_name, fn=filter_func)
