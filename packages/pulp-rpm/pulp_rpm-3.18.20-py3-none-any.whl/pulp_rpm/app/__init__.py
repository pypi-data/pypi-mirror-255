from pulpcore.plugin import PulpPluginAppConfig


class PulpRpmPluginAppConfig(PulpPluginAppConfig):
    """
    Entry point for pulp_rpm plugin.
    """

    name = "pulp_rpm.app"
    label = "rpm"
    version = "3.18.20"
    python_package_name = "pulp-rpm"
