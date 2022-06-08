#coding:utf8

import pandas as pd
import os

landmark = []
images = []

root_dir = './data'

for f_p in os.listdir(root_dir):
    for s_p in os.listdir(os.path.join(root_dir, f_p)):
        for t_p in os.listdir(os.path.join(root_dir, f_p, s_p)):
            for p_p in os.listdir(os.path.join(root_dir, f_p, s_p, t_p)):
                lm = f_p+s_p+t_p+p_p
                landmark.append(lm)
                names = ''
                for name in os.listdir(os.path.join(root_dir, f_p, s_p, t_p, p_p)):
                    names += os.path.join(root_dir, f_p, s_p, t_p, p_p, name)+' '
                names = names[:-1]
                images.append(names)

pd.DataFrame({'landmark_id':landmark, 'images':images}).to_csv('the_clean.csv', index=False)