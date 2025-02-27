"""Manager"""
import logging
from uuid import UUID

from bluetooth_mesh import models

from . import Module


class ManagerModule(Module):
    """
    Node managment functionality
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._get_result = None

    def initialize(self, app, store, config):  # pylint: disable=useless-parent-delegation
        super().initialize(app, store, config)

    def setup_cli(self, parser):
        parser.add_argument("operation")
        parser.add_argument("field")
        parser.add_argument("uuid")

    async def handle_cli(self, args):
        try:
            uuid = UUID(args.uuid)
        except Exception as exp:  # pylint: disable=broad-except
            logging.info(f"Invalid uuid: {exp}")
            return

        node = self.app.nodes.get(uuid)
        if node is None:
            logging.info(f"Unknown node {node}")
            return

        if args.operation == "get":
            if args.field == "ttl":
                await self._get(uuid, node.unicast, "default_ttl")
            if args.field == "composition":
                await self._get(uuid, node.unicast, "composition_data")

            logging.info("Get returned:")
            node.print_info(self._get_result)
            return

        if args.operation == "set":
            return

        logging.info("Unknown operation {args.operation}")

    async def _get(self, uuid, address, getter):
        logging.info(f"Get {getter} from {uuid} ({address})...")

        client = self.app.elements[0][models.ConfigClient]
        getter = getattr(client, f"get_{getter}")
        data = await getter([address], net_index=0)

        self._get_result = data[address]
