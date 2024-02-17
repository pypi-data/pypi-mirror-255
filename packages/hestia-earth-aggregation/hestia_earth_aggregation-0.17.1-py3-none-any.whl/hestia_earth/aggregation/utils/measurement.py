from hestia_earth.schema import MeasurementJSONLD, MeasurementStatsDefinition, MeasurementMethodClassification
from hestia_earth.utils.model import linked_node

from . import _aggregated_version


def _new_measurement(term: dict, value: float = None):
    node = MeasurementJSONLD().to_dict()
    node['term'] = linked_node(term)
    node['methodClassification'] = MeasurementMethodClassification.COUNTRY_LEVEL_STATISTICAL_DATA.value
    if value is not None:
        node['value'] = [value]
        node['statsDefinition'] = MeasurementStatsDefinition.SITES.value
    return _aggregated_version(node, 'term', 'methodClassification', 'statsDefinition', 'value')
