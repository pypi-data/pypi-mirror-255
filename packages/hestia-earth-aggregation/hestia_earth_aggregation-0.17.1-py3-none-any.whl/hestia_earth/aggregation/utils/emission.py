from hestia_earth.schema import EmissionMethodTier
from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name
from hestia_earth.utils.model import find_primary_product

_COLUMN_NAME = 'inHestiaDefaultSystemBoundary'
_ALLOW_ALL = 'all'


def is_in_system_boundary(cycle: dict):
    lookup = download_lookup('emission.csv')
    site_type = cycle.get('site', {}).get('siteType')
    product = find_primary_product(cycle)
    inputs = cycle.get('inputs', [])

    def is_allowed(emission_term_id: str, column: str, condition: str):
        values = get_table_value(lookup, 'termid', emission_term_id, column_name(column))
        values = (values or _ALLOW_ALL).split(';')
        return True if _ALLOW_ALL in values or not condition else condition in values

    def filter_term(term_id: str):
        value = get_table_value(lookup, 'termid', term_id, column_name(_COLUMN_NAME))
        # handle numpy boolean
        return not (not value) and all([
            is_allowed(term_id, 'siteTypesAllowed', site_type),
            is_allowed(term_id, 'productTermTypesAllowed', product.get('term', {}).get('termType')),
            is_allowed(term_id, 'productTermIdsAllowed', product.get('term', {}).get('@id')),
            not inputs or any([
                is_allowed(term_id, 'inputTermTypesAllowed', input.get('term', {}).get('termType')) for input in inputs
            ]),
            not inputs or any([
                is_allowed(term_id, 'inputTermIdsAllowed', input.get('term', {}).get('@id')) for input in inputs
            ])
        ])

    return filter_term


def all_in_system_boundary(cycle: dict):
    lookup = download_lookup('emission.csv')
    # find all emissions in system boundary
    return list(filter(is_in_system_boundary(cycle), list(lookup.termid)))


_DEFAULT_TIER = EmissionMethodTier.TIER_1.value


def get_method_tier(emissions: list):
    values = set([e.get('methodTier', _DEFAULT_TIER) for e in emissions])
    return list(values)[0] if len(values) == 1 else _DEFAULT_TIER
