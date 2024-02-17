"""Store any utilities for plugin."""
from jinja2_ansible_filters.core_filters import FilterModule


def gather_filter_plugins():
    """Gather all filter plugins from ansible-core using their filter_loader of filter plugins they have loaded."""
    found_filters = {}
    ansible_filters = FilterModule().filters()
    for filter_name, filter_func in ansible_filters.items():
        if "ansible" not in filter_name:
            filter_name = f"ansible.builtin.{filter_name}"
        found_filters[filter_name] = filter_func

    return found_filters
