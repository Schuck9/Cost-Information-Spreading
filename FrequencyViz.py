"""
A simple implementation of Cost Information Reputation visualization
@date: 2020.5.22
@author: Tingyu Mo
"""

import os 
import numpy as np
import pandas as pd
import json
from collections import defaultdict
import matplotlib.pyplot as plt


keyName = ["AllC_NotReport","AllC_Report",
			"CondC_NotReport","CondC_Report",
			"AllD_NotReport","AllD_Report",
			"Reputation_Bad","Reputation_Good"
]



class JsonEncoder(json.JSONEncoder):

	def default(self, obj):
		if isinstance(obj, np.integer):
			return int(obj)
		elif isinstance(obj, np.floating):
			return float(obj)
		elif isinstance(obj, np.ndarray):
			return obj.tolist()
		elif isinstance(obj, datetime):
			return obj.__str__()
		else:
			return super(MyEncoder, self).default(obj)

def load_dict(filename):
	'''load dict from json file'''
	with open(filename,"r") as json_file:
		dic = json.load(json_file)
	return dic

def save_dict(filename, dic):
	'''save dict into json file'''
	with open(filename,'w') as json_file:
		json.dump(dic, json_file, ensure_ascii=False, cls=JsonEncoder)


def data_loader(RecordName,Epoch_list = None):

	frequency_dict =defaultdict(list)
	# for key in keyName:
	# 	frequency_dict[key] = []

	frequency_list = os.listdir(RecordName)
	frequency_list.sort()
	del(frequency_list[0])
	for filename in frequency_list:
		frequency_path = os.path.join(RecordName,filename)
		frequency = pd.read_csv(frequency_path,header = None)
		frequency_matrix = frequency.values
		frequency_vector = frequency_matrix.flatten()
		for  i,key in enumerate(keyName):
			frequency_dict[key].append(frequency_vector[i])
	frequency_dict_path = os.path.join(RecordName,"frequency_dict.json")
	save_dict(frequency_dict_path,frequency_dict)
	return frequency_dict

def data_summary():
	data_collect = defaultdict(dict)
	result_path = "./result"
	norm_name = os.listdir(result_path)
	for norm in norm_name:
		norm_path = os.path.join(result_path,norm)
		RecordName_list = os.listdir(norm_path)
		for RecordName in RecordName_list:
			RecordName_path = os.path.join(norm_path,RecordName)
			data_dict = data_loader(RecordName_path)
			data_collect[norm][RecordName] = data_dict
	data_collect_path = os.path.join(result_path,"sumdata_dict.json")
	save_dict(data_collect_path,data_collect)

def viz_all(data):
	#每中cR的每种策略在不同Norm中的图
	info = 'Strategy Frequency'

	# x_label = ["0.5/1","0.5","1"]

	# x_axis = np.log10(x_label)
	norm_name = ["Image_Scoring","Stern_Juding"]
	cR = ["cR_0.00","cR_0.01","cR_0.03"]
	x_axis = np.arange(len(data[norm_name[0]][cR[0]][keyName[0]]))

	plt.figure()	
	for i,cR_ in enumerate(cR):
		for key in keyName:
			plt.clf()
			save_path = "./graph/{}_{}_{}.jpg".format(info,cR_,key)
			# plt.rcParams['font.family'] = ['sans-serif']
			# plt.rcParams['font.sans-serif'] = ['SimHei']
			# plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
			plt.title(" {}  {}  {}".format(info,cR_,key))
			plt.xlabel("Generation × 10^5")#x轴p上的名字
			plt.ylabel("Frequency")#y轴上的名字
			# plt.xticks(x_axis,fontsize=16)
			# plt.plot(x_axis, p_axis,marker='^',linestyle='-',color='skyblue', label='Offer (p)')
			# plt.plot(x_axis, q_axis, marker='s',linestyle='-',color='red', label='Demand (q)')
			# plt.plot(x_axis, y_list[0] ,marker='>',linestyle='-',color='purple', label='w = 0.001')
			plt.plot(x_axis, data[norm_name[0]][cR_][key] ,linestyle='-',color='skyblue', label=norm_name[0])
			plt.plot(x_axis, data[norm_name[1]][cR_][key]  , linestyle='-',color='red', label=norm_name[1])
			# plt.plot(x_axis, data[norm_name[2]][cR_][key] , marker='*',linestyle='-',color='red', label=norm_name[2])
			# plt.plot(x_axis, y_p_list[i+3], marker='*',linestyle='-',color='black', label='WS = 10')	    # plt.plot(x_axis, thresholds, color='blue', label='threshold')
			plt.legend(loc = 'upper right') # 显示图例
			plt.savefig(save_path)
			print("Figure has been saved to: ",save_path)
			# plt.show()

def viz(data):
	#每种Norm的每种策略在不同cR下的图
	info = 'Strategy Frequency'

	# x_label = ["0.5/1","0.5","1"]

	# x_axis = np.log10(x_label)
	norm_name = ["Image_Scoring","Stern_Juding"]
	cR = ["cR_0.00","cR_0.01","cR_0.03"]
	x_axis = np.arange(len(data[norm_name[0]][cR[0]][keyName[0]]))

	plt.figure()	
	
	for  norm_name_ in norm_name:
		for key in keyName:
			plt.clf()
			save_path = "./graph/{}_{}_{}.jpg".format(info,norm_name_,key)
			# plt.rcParams['font.family'] = ['sans-serif']
			# plt.rcParams['font.sans-serif'] = ['SimHei']
			# plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
			plt.title(" {}  {}  {}".format(info,norm_name_,key))
			plt.xlabel("Generation × 10^5")#x轴p上的名字
			plt.ylabel("Frequency")#y轴上的名字
			plt.plot(x_axis, data[norm_name_][cR[0]][key] , linestyle= 'dashdot',color='skyblue', label=cR[0])
			plt.plot(x_axis, data[norm_name_][cR[1]][key]  , linestyle=  'dashdot',color='gold', label=cR[1])
			plt.plot(x_axis, data[norm_name_][cR[2]][key]  , linestyle= 'dashdot',color='black', label=cR[2])


			plt.legend(loc = 'upper right') # 显示图例
			plt.savefig(save_path)
			print("Figure has been saved to: ",save_path)
			# plt.show()


if __name__ == '__main__':
	
	# RecordName ='2020-05-22-20-51' # 0.1
	# frequency_dict = data_loader(RecordName)
	# for key in keyName:
	# 	print("{}:{}".format(key,frequency_dict[key]))
	if not os.path.exists("./result/sumdata_dict.json"):
		data_collect = data_summary()
	else:
		data_collect = load_dict("./result/sumdata_dict.json")
		print("data loaded!")
	viz(data_collect)
	
