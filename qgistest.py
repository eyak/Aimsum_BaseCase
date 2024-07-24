import json


def create_feature(properties):
    return {
        "type": "Feature",
        "geometry": None,  # We're not including geometry in this layer
        "properties": properties
    }

def create_geojson_struct_from_features(features):
    # Create the GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    return geojson



def create_geojson(fn, df):
    # properties = {
    #     "id": 13503242,
    #     "metadata1": f"Info for section ",
    #     "value": 100
    # }

    # get the record for each row in the df, and create a feature
    features = []
    for i, row in df.iterrows():
        properties = row.to_dict()
        feature = create_feature(properties)
        features.append(feature)

    geojson = create_geojson_struct_from_features(features)

    with open('data.geojson', 'w') as f:
        json.dump(geojson, f)


def test():
    import pandas as pd
    df = pd.DataFrame([
        {'id': 13503242, 'metadata1': 'Info for section', 'value': 200},
        ])

    create_geojson('data.geojson', df)
    print('done')


if __name__ == '__main__':
    test()