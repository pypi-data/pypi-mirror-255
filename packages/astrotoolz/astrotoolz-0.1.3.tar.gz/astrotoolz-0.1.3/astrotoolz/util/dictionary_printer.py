import pandas as pd
import numpy as np


def print_dict_as_table(dict_obj, value_extractor, comparison_func):
    keys = list(dict_obj.keys())
    matrix = np.empty((len(keys), len(keys)), dtype=object)
    for i, key1 in enumerate(keys):
        for j, key2 in enumerate(keys):
            # Find the corresponding object
            obj = next(
                (obj for obj in dict_obj[key1] if comparison_func(obj, key2)),
                None,
            )
            matrix[i, j] = round(value_extractor(obj), 3) if obj else ""
    df = pd.DataFrame(matrix, index=keys, columns=keys)
    print(df)
