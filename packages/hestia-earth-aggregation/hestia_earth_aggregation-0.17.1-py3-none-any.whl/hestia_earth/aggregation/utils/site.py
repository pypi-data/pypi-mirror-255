from functools import reduce
from hestia_earth.schema import SchemaType
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.model import linked_node
from hestia_earth.utils.tools import non_empty_list, flatten

from . import _aggregated_version, _aggregated_node, _set_dict_array
from .term import _update_country, _format_country_name
from .measurement import _new_measurement
from .source import format_aggregated_sources


def _format_aggregate(aggregate: dict):
    node = aggregate.get('node')
    term = aggregate.get('term')
    value = aggregate.get('value')
    min = aggregate.get('min')
    max = aggregate.get('max')
    sd = aggregate.get('sd')
    observations = aggregate.get('observations')
    measurement = _new_measurement(term, value)
    _set_dict_array(measurement, 'observations', observations)
    _set_dict_array(measurement, 'min', min)
    _set_dict_array(measurement, 'max', max)
    _set_dict_array(measurement, 'sd', sd, True)
    if node.get('depthUpper') is not None:
        measurement['depthUpper'] = node.get('depthUpper')
    if node.get('depthLower') is not None:
        measurement['depthLower'] = node.get('depthLower')
    return _aggregated_version(measurement, 'min', 'max', 'sd', 'observations', 'depthUpper', 'depthLower')


def _format_aggregated_sites(sites: list):
    all_sites = non_empty_list(flatten([v.get('aggregatedSites', v) for v in sites]))
    return list(map(linked_node, all_sites))


def _format_results(results: tuple):
    aggregates, data = results
    sites = data.get('nodes', [])
    return {
        **_create_site(sites[0]),
        'measurements': list(map(_format_aggregate, aggregates)),
        'aggregatedSites': _format_aggregated_sites(sites),
        'aggregatedSources': format_aggregated_sources(sites, 'defaultSource')
    } if len(sites) > 0 else None


def _site_id(n: dict, include_siteType: bool):
    return '-'.join(non_empty_list([
        _format_country_name(n.get('country', {}).get('name')),
        n.get('siteType') if include_siteType else None
    ]))


def _site_name(n: dict, include_siteType: bool):
    return ' - '.join(non_empty_list([
        n.get('country', {}).get('name'),
        n.get('siteType') if include_siteType else None
    ]))


def _create_site(data: dict, include_siteType=True):
    site = {'type': SchemaType.SITE.value}
    site['country'] = data['country']
    site['siteType'] = data['siteType']
    site['name'] = _site_name(site, include_siteType)
    site['id'] = _site_id(site, include_siteType)
    site['dataPrivate'] = False
    return _aggregated_node(site)


def _update_site(country_name: str, source: dict = None, include_siteType=True):
    def update(site: dict):
        site['country'] = _update_country(country_name) if country_name else site.get('country')
        site['name'] = _site_name(site, include_siteType)
        site['id'] = _site_id(site, include_siteType)
        return site if source is None else {**site, 'defaultSource': source}
    return update


def _should_aggregate_measurement(measurement: dict):
    term = measurement.get('term', {})
    lookup = download_lookup(f"{term.get('termType')}.csv")
    value = get_table_value(lookup, 'termid', term.get('@id'), column_name('arrayTreatmentLargerUnitOfTime'))
    # ignore any measurement with time-split data
    return not value


def _group_by_measurement(group: dict, blank_node: dict):
    key = '-'.join(non_empty_list([
        blank_node.get('term', {}).get('@id'),
        str(blank_node.get('depthUpper', '')),
        str(blank_node.get('depthLower', ''))
    ]))
    if key not in group:
        group[key] = []
    group[key].append(blank_node)
    return group


def _group_by_measurements(sites: list):
    def group_by(group: dict, site: dict):
        group['site']['nodes'].append(site)
        measurements = list(map(
            lambda v: {
                **v,
                'country': site.get('country')
            }, filter(_should_aggregate_measurement, site.get('measurements', []))))
        group['site']['measurements'] = reduce(_group_by_measurement, measurements, group['site']['measurements'])
        return group
    return reduce(group_by, sites, {'site': {'nodes': [], 'measurements': {}}})
