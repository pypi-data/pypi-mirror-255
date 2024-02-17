from unittest.mock import patch

from tests.utils import start_year, end_year
from hestia_earth.aggregation.impact_assessment.utils import _update_impact_assessment

class_path = 'hestia_earth.aggregation.impact_assessment.utils'
country_name = 'Japan'


@patch(f"{class_path}._format_country_name", side_effect=lambda n: n)
@patch(f"{class_path}._update_country", side_effect=lambda v: {'name': v})
@patch(f"{class_path}.download_hestia", return_value={'@id': 'cycle-id'})
@patch(f"{class_path}.node_exists", return_value=False)
def test_update_impact_assessment(fake_node_exists, *args):
    impact = {}
    result = _update_impact_assessment(country_name, start_year, end_year)(impact)
    assert result == {
        'id': f"{country_name}-conventional-non-irrigated-{start_year}-{end_year}",
        'cycle': {'@id': 'cycle-id'},
        'name': f"{country_name} - Conventional, Non Irrigated - {start_year}-{end_year}",
        'country': {
            'name': country_name
        },
        'startDate': str(start_year),
        'endDate': str(end_year),
        'aggregatedQualityScore': 0,
        'aggregatedQualityScoreMax': 3
    }

    # with a source
    source = {'@type': 'Source', '@id': 'source'}
    fake_node_exists.return_value = True
    result = _update_impact_assessment(country_name, start_year, end_year, source)(impact)
    assert result == {
        'id': f"{country_name}-conventional-non-irrigated-{start_year}-{end_year}",
        'cycle': {'@id': 'cycle-id'},
        'name': f"{country_name} - Conventional, Non Irrigated - {start_year}-{end_year}",
        'site': {
            '@type': 'Site',
            '@id': f"{country_name}-conventional-non-irrigated-{start_year}-{end_year}"
        },
        'country': {
            'name': country_name
        },
        'startDate': str(start_year),
        'endDate': str(end_year),
        'source': source,
        'aggregatedQualityScore': 0,
        'aggregatedQualityScoreMax': 3
    }
