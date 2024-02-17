import os
from statistics import stdev
from functools import reduce
from hestia_earth.utils.tools import safe_parse_date, list_sum

from ..version import VERSION
from .term import _group_by_term_id, _group_completeness, is_complete

MIN_NB_OBSERVATIONS = 20


def create_folders(filepath: str): return os.makedirs(os.path.dirname(filepath), exist_ok=True)


def _save_json(data: dict, filename: str):
    import os
    should_run = os.getenv('DEBUG', 'false') == 'true'
    if not should_run:
        return
    import json
    dir = os.getenv('TMP_DIR', '/tmp')
    filepath = f"{dir}/{filename}.jsonld"
    create_folders(filepath)
    with open(filepath, 'w') as f:
        return json.dump(data, f, indent=2)


def _aggregated_node(node: dict):
    return {**node, 'aggregated': True, 'aggregatedVersion': VERSION}


def _aggregated_version(node: dict, *keys):
    node['aggregated'] = node.get('aggregated', [])
    node['aggregatedVersion'] = node.get('aggregatedVersion', [])
    all_keys = ['value'] if len(keys) == 0 else keys
    for key in all_keys:
        if node.get(key) is None:
            continue
        if key in node['aggregated']:
            node.get('aggregatedVersion')[node['aggregated'].index(key)] = VERSION
        else:
            node['aggregated'].append(key)
            node['aggregatedVersion'].append(VERSION)
    return node


def _min(values, observations: int = 0):
    return min(values) if (observations or len(values)) >= MIN_NB_OBSERVATIONS else None


def _max(values, observations: int = 0):
    return max(values) if (observations or len(values)) >= MIN_NB_OBSERVATIONS else None


def _sd(values): return stdev(values) if len(values) >= 2 else None


def _unique_nodes(nodes: list): return list({n.get('@id'): n for n in nodes}.values())


def parse_node_value(value):
    return value if any([value is None, isinstance(value, float), isinstance(value, int)]) else list_sum(value, None)


def sum_values(values: list):
    """
    Sum up the values while handling `None` values.
    If all values are `None`, the result is `None`.
    """
    filtered_values = [v for v in values if v is not None]
    return sum(filtered_values) if len(filtered_values) > 0 else None


def _set_dict_single(data: dict, key: str, value, strict=False):
    if value is not None and (not strict or value != 0):
        data[key] = value
    return data


def _set_dict_array(data: dict, key: str, value, strict=False):
    if data is not None and value is not None and (not strict or value != 0):
        data[key] = [value]
    return data


def _end_date_year(node: dict):
    date = safe_parse_date(node.get('endDate'))
    return date.year if date else None


def _same_product(product: dict):
    def compare(node: dict):
        np = node.get('product', {}) if node else {}
        return np.get('@id', np.get('term', {}).get('@id')) == product.get('@id')
    return compare


GROUP_BY_METHOD_MODEL_PROP = [
    'impacts',
    'endpoints'
]


def _group_by_product(product: dict, nodes: list, props: list, include_matrix=True) -> dict:
    def group_by(group: dict, node: dict):
        node_id = node.get('@id', node.get('id'))
        end_date = _end_date_year(node)
        organic = node.get('organic', False)
        irrigated = node.get('irrigated', False)
        key = '-'.join([str(organic), str(irrigated)]) if include_matrix else ''
        data = {
            'organic': organic,
            'irrigated': irrigated,
            'country': node.get('country'),
            'year': end_date
        }
        if key not in group:
            group[key] = {
                'product': product,
                'nodes': [],
                'sites': [],
                'completeness': {},
                **data,
                **reduce(lambda prev, curr: {**prev, curr: {}}, props, {})
            }
        group[key]['nodes'].append({**node, **data})
        group[key]['sites'].append(node.get('site'))

        def group_by_prop(prop: str):
            # save ref to organic/irrigated for later grouping
            values = list(map(
                lambda v: {
                    **v,
                    **data,
                    'id': node_id,
                    'completeness': is_complete(node, product, v)
                }, node.get(prop, [])))
            return reduce(_group_by_term_id(prop in GROUP_BY_METHOD_MODEL_PROP), values, group[key][prop])

        group[key] = reduce(lambda prev, curr: {**prev, curr: group_by_prop(curr)}, props, group[key])
        group[key]['completeness'] = _group_completeness(group[key]['completeness'], node)
        return group

    return reduce(group_by, list(filter(_same_product(product), nodes)), {})


def value_difference(value: float, expected_value: float):
    """
    Get the difference in percentage between a value and the expected value.

    Parameters
    ----------
    value : float
        The value to check.
    expected_value : float
        The expected value.

    Returns
    -------
    bool
        The difference in percentage between the value and the expected value.
    """
    return 0 if (isinstance(expected_value, list) and len(expected_value) == 0) or expected_value == 0 else (
        round(abs(value - expected_value) / expected_value, 4)
    )
