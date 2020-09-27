import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None


def prices_intervals(plant_table, material_id, price_group_round=0):
    plant_material_table = plant_table[(plant_table['material'] == material_id)]
    plant_material_table['price'] = round(plant_material_table['sales_sum'] / plant_material_table['sales_count'], price_group_round)
    
    price_date = plant_material_table.sort_values(by='chq_date', ascending=True)[['price', 'chq_date']]

    prices = []
    dates = []
    
    current_price = 0
    current_date = ''
    for index, row in price_date.iterrows():
        if (row['price'] != current_price) and (row['chq_date'] != current_date):
            current_price = row['price']
            current_date = row['chq_date']
            prices.append(current_price)
            dates.append(current_date)
    if len(price_date) > 0:
        dates.append(price_date.iloc[-1]['chq_date'])

    return prices, dates


def get_quantity(plant_table, material_id, dates):
    quantity = []
    for i in range(len(dates) - 1):
        sales_count = len(plant_table[(plant_table['material'] == material_id) &\
                                      (plant_table['chq_date'] >= dates[i]) &\
                                      (plant_table['chq_date'] < dates[i + 1])])

        cheques = len(plant_table[(plant_table['chq_date'] >= dates[i]) &\
                                  (plant_table['chq_date'] < dates[i + 1])]['chq_id'].unique())
        if cheques == 0:
            quantity.append(0)
        else:
            quantity.append(sales_count / cheques)
    
    return quantity


def mutual_elasticity(price_prev, price_next, demand_prev, demand_next):
    return (price_prev + price_next) / (demand_prev + demand_next) * \
           (demand_next - demand_prev) / (price_next - price_prev)


def calculate_elasticity(target_tuple, candidate_tuple):
    if len(target_tuple[1]) < 2:
        return (candidate_tuple[0], None)

    elasticity_list = []
    for i in range(len(target_tuple[1]) - 1):
        try:
            elasticity_list.append(mutual_elasticity(target_tuple[1][i], 
                                         target_tuple[1][i + 1], 
                                         candidate_tuple[1][i], 
                                         candidate_tuple[1][i + 1]))
        except ZeroDivisionError:
            continue
    
    if len(elasticity_list) == 0:
        return (candidate_tuple[0], None)

    mean_elasticity = np.array(elasticity_list).mean()
    
    return (candidate_tuple[0], mean_elasticity)


def calculate_elasticities(target_tuple, candidates_list):
    '''
    input: (id, prices), [(id, quantities), (...), ...]
    output: [(id, mean_elasticities), (...), ...]] which is ranked
    '''
    output_list = []
    for candidate_tuple in candidates_list:
        elasticity_tuple = calculate_elasticity(target_tuple, candidate_tuple)
        if (elasticity_tuple[1] and elasticity_tuple[1] > 0):
            output_list.append(elasticity_tuple)
    
    output_list = sorted(output_list, key = lambda x: x[1], reverse=True)
    
    return output_list
