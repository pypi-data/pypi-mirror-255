import argparse

from hacktegic._internal.commands.networks.create import NetworksCreateCommand
from hacktegic._internal.commands.networks.delete import NetworksDeleteCommand
from hacktegic._internal.commands.networks.describe import NetworksDescribeCommand
from hacktegic._internal.commands.networks.update import NetworksUpdateCommand
from hacktegic._internal.commands.networks.list import NetworksListCommand
from hacktegic._internal.commands.auth.login import LoginCommand
from hacktegic._internal.commands.auth.logout import LogoutCommand
from hacktegic._internal.commands.auth.register import RegisterCommand
from hacktegic._internal.commands.config.get import ConfigGetCommand
from hacktegic._internal.commands.config.set import ConfigSetCommand
from hacktegic._internal.commands.projects.create import ProjectsCreateCommand
from hacktegic._internal.commands.projects.delete import ProjectsDeleteCommand
from hacktegic._internal.commands.projects.describe import ProjectsDescribeCommand
from hacktegic._internal.commands.projects.list import ProjectsListCommand
from hacktegic._internal.commands.projects.update import ProjectsUpdateCommand
from hacktegic._internal.commands.scanprofiles.create import ScanProfilesCreateCommand
from hacktegic._internal.commands.scanprofiles.delete import ScanProfilesDeleteCommand
from hacktegic._internal.commands.scanprofiles.describe import ScanProfilesDescribeCommand
from hacktegic._internal.commands.scanprofiles.list import ScanProfilesListCommand
from hacktegic._internal.commands.scanprofiles.update import ScanProfilesUpdateCommand
from hacktegic._internal.commands.scanprofiles.networks_list import ScanProfilesNetworksListCommand
from hacktegic._internal.commands.scanprofiles.networks_attach import ScanProfilesNetworksAttachCommand
from hacktegic._internal.commands.scanprofiles.networks_detach import ScanProfilesNetworksDetachCommand
from hacktegic._internal.commands.scanprofiles.portscans_run import ScanProfilesOnDemandScanCommand
from hacktegic._internal.commands.portscans.list import PortScansListCommand
from hacktegic._internal.commands.portscans.describe import PortScansDescribeCommand
from hacktegic._internal.commands.portscans.delete import PortScansDeleteCommand

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.description = "HackTegic CLI tool"
        self.epilog = "For more information, visit https://github.com/hacktegic"

    def add_arguments(self):
        subparsers = self.add_subparsers()

        # Authentication commands
        self._setup_auth_commands(subparsers)

        # Project commands
        self._setup_project_commands(subparsers)

        # Configuration commands
        self._setup_config_commands(subparsers)

        # Network commands
        self._setup_network_commands(subparsers)

        # Scan Profile commands
        self._setup_scanprofile_commands(subparsers)

        # Port Scan commands
        self._setup_portscans_commands(subparsers)

    def _setup_auth_commands(self, subparsers):
        auth_parser = subparsers.add_parser("auth", help="authentication commands")
        auth_subparsers = auth_parser.add_subparsers(help="auth sub-command help")

        self._add_command(auth_subparsers, "login", LoginCommand)
        self._add_command(auth_subparsers, "logout", LogoutCommand)
        self._add_command(auth_subparsers, "register", RegisterCommand)

    def _setup_project_commands(self, subparsers):
        projects_parser = subparsers.add_parser("projects", help="project commands")
        projects_subparsers = projects_parser.add_subparsers(
            help="project sub-command help"
        )

        self._add_command(
            projects_subparsers, "create", ProjectsCreateCommand, "project_name",
            description="Create a new HackTegic project by providing the project name.\n\nUsage: python3 hacktegic projects create my-project"
        )
        self._add_command(
            projects_subparsers, "describe", ProjectsDescribeCommand, "project_id",
            description="Describe a specific HackTegic project by providing the project ID.\n\nUsage: python3 hacktegic projects describe 1234"
        )
        self._add_command(projects_subparsers, "list", ProjectsListCommand)
        self._add_command(
            projects_subparsers,
            "update",
            ProjectsUpdateCommand,
            "project_id",
            "--name",
            description="Update a specific HackTegic project by providing the project ID and the new project name.\n\nUsage: python3 hacktegic projects update 1234 --name my-project"
        )
        self._add_command(
            projects_subparsers, "delete", ProjectsDeleteCommand, "project_id",
            description="Delete a specific HackTegic project by providing the project ID.\n\nUsage: python3 hacktegic projects delete 1234"
        )
        projects_parser.description = "HackTegic projects management command"

    def _setup_config_commands(self, subparsers):
        config_parser = subparsers.add_parser("config", help="config help")
        config_subparsers = config_parser.add_subparsers(help="config sub-command help")

        self._add_command(config_subparsers, "get", ConfigGetCommand, "key")
        self._add_command(config_subparsers, "set", ConfigSetCommand, "key", "value")


    def _setup_network_commands(self, subparsers):
        networks_parser = subparsers.add_parser("networks", help="network commands")
        networks_subparsers = networks_parser.add_subparsers(
            help="network sub-command help"
        )

        self._add_command(
            networks_subparsers, "create", NetworksCreateCommand, "address", "--description",
            description="Create a new network with the specified address and optional description.\n"
                        "Usage example: python3 hacktegic networks create 192.168.0.0/16 --description 'Internal network'"
        )
        self._add_command(
            networks_subparsers, "list", NetworksListCommand, description="List all networks."
        )
        self._add_command(
            networks_subparsers, "describe", NetworksDescribeCommand, "network_id",
            description="Describe a specific network by providing its ID.\n"
                        "Usage example: python3 hacktegic networks describe 1234"
        )
        self._add_command(
            networks_subparsers,"update", NetworksUpdateCommand, "network_id", "--address", "--description",
            description="Update a specific network by providing its ID and the new address and optional description.\n"
                        "Usage example: python3 hacktegic networks update 1234 192.168.0.0/16 --description 'Internal network'"
        )
        self._add_command(
            networks_subparsers, "delete", NetworksDeleteCommand, "network_id",
            description="Delete a specific network by providing its ID.\n"
        )
        networks_parser.description = "HackTegic networks management command.\n Use sub-commands to create, list, describe, update, and delete networks."

    def _setup_scanprofile_commands(self, subparsers):
        scanprofiles_parser = subparsers.add_parser(
            "scanprofiles", help="scanprofiles commands"
        )

        scanprofiles_subparsers = scanprofiles_parser.add_subparsers(
            help="scanprofiles sub-command help"
        )

        self._add_command(
            scanprofiles_subparsers, "create", ScanProfilesCreateCommand, "--title", "--description", "--schedule", "--enabled", "--nmap_options", "--project_id",
            description="Create a new scan profile with the specified title and optional description.\n"
        )
        self._add_command(
            scanprofiles_subparsers, "list", ScanProfilesListCommand,
            description="List all scan profiles."
        )
        self._add_command(
            scanprofiles_subparsers, "describe", ScanProfilesDescribeCommand, "scanprofile_id",
            description="Describe a specific scan profile by providing its ID.\n"
        )
        self._add_command(
            scanprofiles_subparsers, "update", ScanProfilesUpdateCommand, "scanprofile_id", "--title", "--description", "--schedule", "--enabled", "--nmap_options",
            description="Update a specific scan profile by providing its ID and the new title and/or description.\n"
        )
        self._add_command(
            scanprofiles_subparsers, "delete", ScanProfilesDeleteCommand, "scanprofile_id",
            description="Delete a specific scan profile by providing its ID.\n"
        )
        self._add_command(
            scanprofiles_subparsers, "networks_list", ScanProfilesNetworksListCommand, "scanprofile_id",
            description="List all Networks associated with the specified scan profile.\n"
        )
        self._add_command(
            scanprofiles_subparsers, "networks_attach", ScanProfilesNetworksAttachCommand, "scanprofile_id", "network_id",
            description="Attach a Networks to the specified scan profile.\n"
        )
        self._add_command(
            scanprofiles_subparsers, "networks_detach", ScanProfilesNetworksDetachCommand, "scanprofile_id", "network_id",
            description="Detach a Networks from the specified scan profile.\n"
        )
        self._add_command(
            scanprofiles_subparsers, "portscans_run", ScanProfilesOnDemandScanCommand, "scanprofile_id",
            description="Trigger an on-demand scan for the specified scan profile.\n"
        )

    def _setup_portscans_commands(self, subparsers):
        portscans_parser = subparsers.add_parser(
            "portscans", help="portscans commands"
        )

        portscans_subparsers = portscans_parser.add_subparsers(
            help="portscans sub-command help"
        )

        self._add_command(
            portscans_subparsers, "list", PortScansListCommand,
            description="List all port scans."
        )
        self._add_command(
            portscans_subparsers, "describe", PortScansDescribeCommand, "portscan_id",
            description="Describe a specific port scan by providing its ID.\n"
        )
        self._add_command(
            portscans_subparsers, "delete", PortScansDeleteCommand, "portscan_id",
            description="Delete a specific port scan by providing its ID.\n"
        )

    def _add_command(self, subparsers, name, command_class, *args, description=None):
        parser = subparsers.add_parser(name, help=f"{name} help", formatter_class=argparse.RawDescriptionHelpFormatter)
        parser.description = description
        parser.set_defaults(func=command_class.run)
        for arg in args:
            parser.add_argument(arg, type=str)
