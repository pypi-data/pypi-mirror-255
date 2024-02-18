import logging

import dotenv

dotenv.load_dotenv()
logging.basicConfig(level=logging.CRITICAL)  # here to prevent log.WARN clutter

from .search.client import SearchClient
from .melting.client import MFClient
from .plugins.client import PluginClient
from .private_workspaces.client import PrivateWorkspaceClient

__all__ = ["SearchClient", "MFClient", "PluginClient", "PrivateWorkspaceClient"]
