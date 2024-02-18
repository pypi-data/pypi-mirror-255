from ..exceptions import TeiaSdkError


class ErrorToGetPluginInfo(TeiaSdkError):
    """Error to get plugin info"""


class ErrorToGetPluginResponse(TeiaSdkError):
    """Error to get plugin info"""


class ErrorPluginAPISelectAndRun(TeiaSdkError):
    """API was not able to select and run plugins"""


class PluginSelectionNotFound(TeiaSdkError):
    """API was not able to find the plugin selection object"""


class PluginExecutionNotFound(TeiaSdkError):
    """API was not able to find the plugin execution object"""


class ErrorGetPluginSelection(TeiaSdkError):
    """API was not able to select and run plugins"""


class ErrorGetPluginExecution(TeiaSdkError):
    """API was not able to select and run plugins"""
