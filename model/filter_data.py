import pandas as pd
import numpy as np
import os

raw_df = pd.read_csv('./the_clean.csv')
print(raw_df['images'])

landmark_id = []
path = []

for index, row in raw_df.iterrows():
    ps = str(row['images']).split(' ')
    for p in ps:
        landmark_id.append(row['landmark_id'])
        path.append(p)

print(len(set(landmark_id)))

pd.DataFrame({'landmark_id':landmark_id, 'id':path}).to_csv('./finnal_the_clean.csv', index=False)
