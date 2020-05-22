"""
A simple implementation of Cost Information Reputation visualization
@date: 2020.5.22
@author: Tingyu Mo
"""

import os 
import numpy as ny
import pandas as pd

keyName = ["AllC_NotReport","AllC_Report",
			"CondC_NotReport","CondC_Report",
			"AllD_NotReport","AllD_Report",
			"Reputation_Bad","Reputation_Good"
]

def data_loader(RecordName,Epoch_list = None):

	frequency_dict =dict()
	for key in keyName:
		frequency_dict[key] = []

	frequency_list = os.listdir(RecordName)
	frequency_list.sort()
	for filename in frequency_list:
		frequency_path = os.path.join(RecordName,filename)
		frequency = pd.read_csv(frequency_path,header = None)
		frequency_matrix = frequency.values
		frequency_vector = frequency_matrix.flatten()
		for  i,key in enumerate(keyName):
			frequency_dict[key].append(frequency_vector[i])

	return frequency_dict



if __name__ == '__main__':
	RecordName ='2020-05-22-20-51' # 0.1
	frequency_dict = data_loader(RecordName)
	# for key in keyName:
	# 	print("{}:{}".format(key,frequency_dict[key]))
