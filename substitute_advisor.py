import os

from tabulate import tabulate
from utils import (get_root,
                   get_query_params,
                   hierarchy_level_materials,
                   plant_table)
from elasticity import (prices_intervals,
                        get_quantity,
                        calculate_elasticities)
from suggestions_utils import find_extremes_and_do_promo_suggests


def main():
    root = get_root()
    query_params = get_query_params(root)
    plant_id, material_id, dates_interval = (query_params['plant_id'],
                                             query_params['material_id'],
                                             query_params['dates_interval'])
    
    appropriate_materials = hierarchy_level_materials(materials_table_path=root + os.sep + 'hack_data' + os.sep + 'materials.csv',
                                                      material_id=material_id,
                                                      hierarchy_level=3)
    
    plant = plant_table(transactions_table_path=root + os.sep + 'hack_data' + os.sep + 'transactions.parquet',
                        plant_id=plant_id,
                        dates_interval=dates_interval)
    
    prices, dates = prices_intervals(plant, material_id, price_group_round=0)
    candidates = []
    for material in appropriate_materials:
        candidates.append((material, get_quantity(plant, material, dates)))
    
    substitutes = calculate_elasticities(target_tuple=(material_id, prices),
                                         candidates_list=candidates)

    recommendations = find_extremes_and_do_promo_suggests(material_id, [item[0] for item in substitutes], plant,
                                                          strategy='lightfm', verbose=False)
    
    print('\nWe believe that Lenta for store: {}\n'.format(plant_id) +\
          'to offer the following subtitutes for the following clients\n' +\
          'with a personal discount:')
    
    print(tabulate(recommendations, headers='keys', tablefmt='psql'))


if __name__ == "__main__":
    main()
