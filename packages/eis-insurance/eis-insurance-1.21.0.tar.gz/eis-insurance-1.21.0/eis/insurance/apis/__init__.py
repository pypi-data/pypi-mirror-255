
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from eis.insurance.api.insured_object_types_api import InsuredObjectTypesApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from eis.insurance.api.insured_object_types_api import InsuredObjectTypesApi
from eis.insurance.api.insured_objects_api import InsuredObjectsApi
from eis.insurance.api.lead_statuses_api import LeadStatusesApi
from eis.insurance.api.leads_api import LeadsApi
from eis.insurance.api.named_ranges_api import NamedRangesApi
from eis.insurance.api.policies_api import PoliciesApi
from eis.insurance.api.premium_formulas_api import PremiumFormulasApi
from eis.insurance.api.product_factors_api import ProductFactorsApi
from eis.insurance.api.product_fields_api import ProductFieldsApi
from eis.insurance.api.product_versions_api import ProductVersionsApi
from eis.insurance.api.products_api import ProductsApi
from eis.insurance.api.default_api import DefaultApi
