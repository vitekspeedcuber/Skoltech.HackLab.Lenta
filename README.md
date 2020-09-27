# Skoltech.HackLab.Lenta

## Diverse Universe Team

## Idea

* Initially, we limit the possible replacement products by choosing the hierarchy level. So, we can get **appropriate candidates**.

* Then we create table for entered fixed interval of dates and particular store (plant).

* Using such an economic concept as **cross-elasticity**, we calculate the coefficients of interchangeability for all pairs
  of our target material and appropriate others.

* As a final chord, we select among the **substitute products** found, those that are most suitable for each of the **extreme clients**.

## Running

Initially, we should choose the particular store and material for which we want to find substitutes in the `query.yaml` file:

```
plant_id: a9dd14d824822d6d78d0fe3e55dbd7fb # ID of store
material_id: 3a57e118023712eb5876864815796a78 # ID of material (item)
dates_interval: 2016-10-04, 2017-10-04 # start and end dates of the considered time interval
```

Then we should run `substitute_advisor.py` file:

```
python substitute_advisor.py --root=<path_to_the_project>
```

### Results Example

After running `substitute_advisor.py` file you will get similar output:

![output_example](output_example.png)
