from unittest.mock import patch
from hestia_earth.schema import SiteSiteType, TermTermType

from hestia_earth.aggregation.utils.emission import all_in_system_boundary

class_path = 'hestia_earth.aggregation.utils.emission'


@patch(f"{class_path}.find_primary_product")
def test_all_in_system_boundary_cropland(mock_primary_product):
    cycle = {'site': {}}

    mock_primary_product.return_value = {
        'term': {
            '@id': 'wheatGrain',
            'termType': TermTermType.CROP.value
        }
    }
    cycle['site']['siteType'] = SiteSiteType.CROPLAND.value
    term_ids = all_in_system_boundary(cycle)
    assert len(term_ids) > 50

    mock_primary_product.return_value = {
        'term': {
            '@id': 'ricePlantFlooded',
            'termType': TermTermType.CROP.value
        }
    }
    cycle['site']['siteType'] = SiteSiteType.CROPLAND.value
    term_ids = all_in_system_boundary(cycle)
    assert len(term_ids) > 50

    # with inputs restriction, we should have less emissions
    cycle['inputs'] = [
        {
            'term': {'termType': 'crop'}
        }
    ]
    cycle['site']['siteType'] = SiteSiteType.CROPLAND.value
    assert len(all_in_system_boundary(cycle)) < len(term_ids)


@patch(f"{class_path}.find_primary_product")
def test_all_in_system_boundary_animal_housing(mock_primary_product):
    cycle = {'site': {}}

    mock_primary_product.return_value = {
        'term': {
            '@id': 'meatBeefCattleLiveweight',
            'termType': TermTermType.ANIMALPRODUCT.value
        }
    }
    cycle['site']['siteType'] = SiteSiteType.ANIMAL_HOUSING.value
    term_ids = all_in_system_boundary(cycle)
    assert len(term_ids) > 20
