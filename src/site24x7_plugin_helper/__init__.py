'''
    This is the helper module for site24x7 plugin integration.

    Example usage:
    >>> from site24x7_plugin_helper.connector.cache_client import CacheClient
    >>> CacheClient = CacheClient(
    >>>     '/tmp/default.cache',
    >>>     author='Renas Mirkan Kilic',
    >>>     plugin_version="1",
    >>>     date_created='Aug 19th, 2022'
    >>> )
    >>> CacheClient.set_metric_types()
    >>> CacheClient.dumps(CacheClient.dict)
    >>> {
    >>>     "author": "Renas Mirkan Kilic",
    >>>     "plugin_version": "1",
    >>>     "date_created": "Aug 19th, 2022",
    >>>     "units": {...}
    >>> }
'''
