
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from eis.claim.api.claim_statuses_api import ClaimStatusesApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from eis.claim.api.claim_statuses_api import ClaimStatusesApi
from eis.claim.api.claims_api import ClaimsApi
from eis.claim.api.settlements_api import SettlementsApi
from eis.claim.api.default_api import DefaultApi
