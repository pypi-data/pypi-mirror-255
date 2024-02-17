from functools import reduce
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data_closest_date
from hestia_earth.utils.tools import non_empty_list, safe_parse_float, flatten

from hestia_earth.aggregation.log import debugWeights, debugRequirements
from hestia_earth.aggregation.utils import parse_node_value, _end_date_year, _min, _max, _sd
from hestia_earth.aggregation.utils.term import (
    DEFAULT_COUNTRY_ID, _blank_node_completeness, _format_organic, _format_irrigated
)


def _organic_weight(country_id: str, year: int):
    lookup = download_lookup('region-standardsLabels-isOrganic.csv')
    data = get_table_value(lookup, 'termid', country_id, 'organic')
    # default to 0 => assume nothing organic
    value = safe_parse_float(extract_grouped_data_closest_date(data, year), None)

    debugRequirements(country_id=country_id, year=year,
                      organic_weight=value)

    return min(1, value / 100) if value else None


def _irrigated_weight(country_id: str, year: int, siteType: str = 'all'):
    lookup = download_lookup('region-irrigated.csv')

    total_area_data = get_table_value(lookup, 'termid', country_id, column_name(siteType))
    # default to 1 => assume whole area
    total_area = safe_parse_float(extract_grouped_data_closest_date(total_area_data, year), 1)

    irrigated_data = get_table_value(lookup, 'termid', country_id, column_name(f"{siteType} irrigated"))
    irrigated = safe_parse_float(extract_grouped_data_closest_date(irrigated_data, year), None)

    debugRequirements(country_id=country_id, year=year,
                      site_type=siteType,
                      total_area=total_area,
                      irrigated_area=irrigated)

    return irrigated / total_area if irrigated else None


def _add_weights(country_id: str, year: int):
    def apply(prev: dict, node: dict):
        organic_weight = _organic_weight(country_id, year) or _organic_weight(DEFAULT_COUNTRY_ID, year)
        irrigated_weight = (
            _irrigated_weight(country_id, year, 'cropland') or
            _irrigated_weight(country_id, year, 'agriculture') or
            _irrigated_weight(country_id, year) or
            0
        )
        weight = (
            organic_weight if node.get('organic', False) else 1-organic_weight
        ) * (
            irrigated_weight if node.get('irrigated', False) else 1-irrigated_weight
        )
        return {**prev, node.get('id'): {'weight': weight, 'completeness': node.get('completeness', {})}}
    return apply


def _weighted_value(weights: dict, key: str = 'value'):
    def apply(node: dict):
        value = parse_node_value(node.get(key))
        weight = weights.get(node.get('id'), {}).get('weight')
        return None if (value is None or weight is None) else (value, weight)
    return apply


def _missing_weights(nodes: list):
    completeness_key = _blank_node_completeness(nodes[0])
    keys = ['-'.join([
        _format_organic(node.get('organic')), _format_irrigated(node.get('irrigated'))
    ]) for node in nodes]

    def apply(item: tuple):
        key, weight = item
        is_complete = weight.get('completeness', {}).get(completeness_key, False)
        is_missing = all([k not in key for k in keys])
        return (0, weight.get('weight')) if is_complete and is_missing else None
    return apply


def _aggregate_weighted(term: dict, nodes: list, weights: dict):
    # account for complete missing values
    missing_weights = non_empty_list(map(_missing_weights(nodes), weights.items()))

    values = non_empty_list(map(_weighted_value(weights), nodes)) + missing_weights

    observations = sum(flatten([n.get('observations', 1) for n in nodes])) + len(missing_weights)

    total_weight = sum(weight for _v, weight in values)
    weighted_values = [value * weight for value, weight in values]
    value = sum(weighted_values) / (total_weight if total_weight != 0 else 1)

    # get min/max from weighted min/max values
    min_values = [v for v, _w in non_empty_list(map(_weighted_value(weights, 'min'), nodes))]
    max_values = [v for v, _w in non_empty_list(map(_weighted_value(weights, 'max'), nodes))]

    return {
        'nodes': nodes,
        'node': nodes[0],
        'term': term,
        'value': value if len(values) > 0 else None,
        'min': _min(min_values if len(min_values) else weighted_values, observations),
        'max': _max(max_values if len(min_values) else weighted_values, observations),
        'sd': _sd(weighted_values),
        'observations': observations
    }


def _aggregate_nodes(aggregate_key: str, weights: dict):
    def aggregate(data: dict):
        def aggregate(term_id: str):
            blank_nodes = data.get(aggregate_key).get(term_id)
            term = blank_nodes[0].get('term')
            return _aggregate_weighted(term, blank_nodes, weights)

        aggregates = flatten(map(aggregate, data.get(aggregate_key, {}).keys()))
        return (aggregates, data) if len(aggregates) > 0 else ([], {})

    def aggregate_multiple(data: dict):
        return reduce(
            lambda prev, curr: {**prev, curr: _aggregate_nodes(curr, weights)(data)}, aggregate_key, {}
        )

    return aggregate if isinstance(aggregate_key, str) else aggregate_multiple


def aggregate(aggregate_key: str, groups: dict) -> list:
    nodes = next((data.get('nodes') for data in groups.values() if len(data.get('nodes', [])) > 0), [])
    first_node = nodes[0]
    country_id = first_node.get('country').get('@id')
    year = _end_date_year(first_node)
    weights = reduce(_add_weights(country_id, year), nodes, {})
    debugWeights(weights)
    return non_empty_list(map(_aggregate_nodes(aggregate_key, weights), groups.values()))
