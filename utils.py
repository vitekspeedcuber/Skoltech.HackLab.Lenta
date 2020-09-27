import argparse
import yaml
import os
import pandas as pd


def get_root():
    root = "."

    parser = argparse.ArgumentParser(description="root path", add_help=True)
    parser.add_argument("--root", type=str, help="path to the project")
    if parser.parse_args().root is not None:
        root = parser.parse_args().root

    return root


def get_query_params(root):
    with open(root + os.sep + 'query.yaml', "r") as config_file:
        configs = yaml.load(config_file, Loader=yaml.FullLoader)

    query_params = {'plant_id': str(configs['plant_id']),
                    'material_id': str(configs['material_id']),
                    'dates_interval': tuple(map(str, configs['dates_interval'].split(', ')))}

    return query_params


def hierarchy_level_materials(materials_table_path, material_id, hierarchy_level=4):
    materials = pd.read_csv(materials_table_path)
    
    hierarchy_level_id = materials[materials['material'] == material_id].iloc[0]['hier_level_' + str(hierarchy_level)]
    appropriate_materials = list(materials[materials['hier_level_' + str(hierarchy_level)] == hierarchy_level_id]['material'].unique())
    appropriate_materials.remove(material_id)
    
    return appropriate_materials


def plant_table(transactions_table_path, plant_id, dates_interval=('2017-06-01', '2017-08-31')):
    transactions_table = pd.read_parquet(transactions_table_path,
                                         engine='pyarrow',
                                         use_threads=True,
                                         columns=['chq_id', 'plant', 'chq_date', 'client_id',
                                                  'material', 'sales_count', 'sales_sum', 'is_promo'])
    
    plant = transactions_table[(transactions_table['plant'] == plant_id) &\
                               (transactions_table['is_promo'] == 0) &\
                               (transactions_table['sales_count'] > 0) &\
                               (transactions_table['chq_date'] >= dates_interval[0]) &\
                               (transactions_table['chq_date'] <= dates_interval[1])].drop(columns=['is_promo'])
    
    return plant
