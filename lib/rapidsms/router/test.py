"""
Router that can be used for testing
"""

from rapidsms.router.blocking import BlockingRouter


class TestRouter(BlockingRouter):
    """ BlockingRouter that doesn't load apps and backends by default """

    def __init__(self, *args, **kwargs):
        """
        Allow apps and backends to be customized, otherwise leave empty
        """
        kwargs['apps'] = kwargs.get('apps', [])
        kwargs['backends'] = kwargs.get('backends', {})
        super(TestRouter, self).__init__(*args, **kwargs)
