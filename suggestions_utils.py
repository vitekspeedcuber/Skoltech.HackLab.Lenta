import numpy as np
import pandas as pd

from lightfm import LightFM
from lightfm.data import Dataset
from lightfm.evaluation import precision_at_k
from sklearn.model_selection import train_test_split


def find_extremes_and_do_promo_suggests(material_id, substitutes, plant_table,
                                        strategy='most_popular', verbose=False):
    
    '''Find extreme users who buy only the targeted product but don't want to buy any of the substitute products, 
       come up with a personalized discount advice for the closest preferred replacement product to our target.
    '''
    client_choices = plant_table.loc[plant_table.material.isin(substitutes + [material_id])].groupby(['client_id'])['material'].value_counts().unstack().fillna(0)
    client_choices['target_freq'] = client_choices[material_id] / client_choices[substitutes].sum(axis=1)

    if verbose:
        print(f'client_choices.shape before {client_choices.shape}')

    client_choices = client_choices.loc[client_choices[material_id] > 2]
    client_choices = client_choices.loc[client_choices['target_freq'] > 0.2]

    if verbose:
        print(f'client_choices.shape after {client_choices.shape}')

    recommendations = pd.DataFrame(index=client_choices.index, columns=['material'])

    if strategy == 'most_popular':
        counts = plant_table.loc[plant_table.material.isin(substitutes)].material.value_counts() 
        most_popular = counts.drop(material_id).index[0]
        recommendations['material'] = most_popular

    if strategy == 'lightfm':
        dataset = Dataset()
        transac = plant_table.loc[plant_table.material.isin(substitutes)]   

        dataset.fit(transac.client_id.unique(), transac.material.unique())
        interactions = [(i['client_id'], i['material']) for iter, i in transac.iterrows()]
        train_interactions, valid_interactions = train_test_split(interactions, train_size=0.8)

        train_interactions_matrix, train_weights_matrix = dataset.build_interactions(train_interactions)
        valid_interactions_matrix, valid_weights_matrix = dataset.build_interactions(valid_interactions)

        model = LightFM(no_components=5, loss='bpr')

        model.fit(train_interactions_matrix, epochs=20)

        # print("Train precision: %.2f" % precision_at_k(model, train_interactions_matrix, k=3).mean())
        # print("Test precision: %.2f" % precision_at_k(model, valid_interactions_matrix, k=3).mean())

        ids_to_nums = pd.Series(index=transac.client_id.unique(), data=np.arange(len(transac.client_id.unique())))[client_choices.index]
        materials_id_preds = model.predict_rank(valid_interactions_matrix).toarray().max(axis=1)
        recommendations['material'] = [substitutes[int(i)] for i in materials_id_preds[ids_to_nums]]

    
    if verbose:
        print(f'''\nHello, honey! 
            \n I see you buy {material_id} sometimes. Unfortunaly we haven't on stock it. \n 
            Don't worry, we have something that can substitute it with sweet special promo for you!''')

    return recommendations
