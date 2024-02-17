from rhessys_calibrater_utils import *
import os

template = '/Users/royzhang/Documents/Github/rhessys_calibration/demo/param_template.csv'

# The default setting, could be modified as needed
para_dict = {'gw1':(0.001,0.2),
            'gw2':(0.001,0.2),
            'gw3':(0.001,0.2),
            's1':(0.001,20),
            's2':(0.1,300.0),
            's3':(0.1,20),
            'sv1':(0.001,20),
            'sv2':(0.1,300.0),
            'svalt1':(0.5,2),
            'svalt2':(0.5,2),
            # 'snowEs ':(0.5,2),
            # 'snowTs ':(0.5,2)
            }

calibrater = rhessys_calibrater(template=template, para_dic=para_dict)  # para_dict = para_dict if customized the ranges

#  2. Create parameter list as csv
calibrater.UniformSample()

# print(calibrater.lines) should be 0

#  3. Generate command lines based on the uniform sampling
#     Note: jobfiles will be saved to folder "jobfiles" under your work_dir

## Uncomment below on HPC
calibrater.JobScripts() # submit=True to submit on Rivanna


cluster = rhessys_cluster(template)

cluster.analyzing_param()
cluster.KclusterSampling('nse', 
                         threshold=0.5)