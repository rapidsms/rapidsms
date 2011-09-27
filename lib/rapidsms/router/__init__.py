#from .legacy import LegacyRouter as Router
from .blocking import BlockingRouter as Router

# a single instance of the router singleton is available globally, like
# the db connection. it shouldn't be necessary to muck with this very
# often (since most interaction with the Router happens within an App or
# Backend, which have their own .router property), but when it is, it
# should be done via this process global
router = Router()
