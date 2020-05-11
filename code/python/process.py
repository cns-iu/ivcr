"""
Construct the skill similarity graph
"""
from sklearn.metrics.cluster import adjusted_mutual_info_score,mutual_info_score
from sklearn.metrics.pairwise import cosine_similarity
from scipy import spatial

from tqdm import tqdm, trange
import heapq
from collections import defaultdict
import pickle
import pandas as pd 

'''
select skills cooccurs with each other
'''
def select_cooccur_skill(input_file):
	skill_set = set()
	with open(input_file) as f:	
		for line in f:
			result = line.rstrip().split(",")
			skill_set.add(result[0])
			skill_set.add(result[1])
	return skill_set
'''
load data as a list of tuples (uid,vector)
'''
def load_data(input_file,skill_set):
	data = []
	df = pd.read_csv(input_file).values.tolist()
	count = 0
	for row in df:
		count += 1
		# if count == 100:
		# 	break
		skill = row[0].replace(" ","_")
		if skill in skill_set:
			vector = [float(row[i]) for i in range(1,len(row))]
			# vector = [v/sum(vector) for v in vector] #normalized vector
			data.append((skill,vector)) 
	
	return data 

'''
calculate skill pairwise adjust mutual information score, 
store the calculated score_map into pickle
'''
def get_ami(data,output_file):
	ami_dict = defaultdict(list)
	for i in trange(len(data)-1):
		curr_skill = data[i][0]
		curr_vec = data[i][1]
		for j in range(i+1,len(data)):
			temp_skill = data[j][0]
			temp_vec = data[j][1]
			ami_score = 1 - spatial.distance.cosine(curr_vec, temp_vec)#mutual_info_score(curr_vec, temp_vec)
			ami_dict[curr_skill].append([ami_score,temp_skill]) #store other skills current ami to skill
			ami_dict[temp_skill].append([ami_score,curr_skill]) 
	return ami_dict

'''
for each skill, rank the top 10 relevant skills with highest ami scores 
store in local disk as graph.
edge direction is from most smiliar skill ---> current skill
'''
def rank_ami(ami_dict, output_file, topK): 
	bw = open(output_file, 'w')
	count = 0
	for skill, ami_l in ami_dict.items():
		count += 1
		if count %500 == 0:
			print(count)
		top_skills = heapq.nlargest(topK, ami_l)
		for [ami_score,curr_skill] in top_skills:
			bw.write(skill + "," + curr_skill + "," + str(ami_score) + "\n")
	bw.close()

def test():
	# a = [2931469.0, 3802872.0, 4073214.0, 5032059.0, 5336082.0, 6096511.0, 6449659.0, 6265005.0, 8401145.0, 1438397.0]
	# b = [1,1,2,3,2,1,0,0,1,1]
	# c = [1,1,1,0,1,2,1,1,2,1]
	# print(mutual_info_score(a, b),mutual_info_score(a, c),mutual_info_score(b, c))
	result = 1 - spatial.distance.cosine([3, 45, 7, 2], [2, 54, 13, 15])
	print(result)
if __name__ == "__main__": 
	skill_set = select_cooccur_skill("../data/cooccur.csv")
	print(len(skill_set))
	data = load_data("../data/skill_count_by_year.csv",skill_set) 
	# print(data[:2])
	print(len(data))
	ami_dict = get_ami(data,"../result/ami_dict.pkl")
	rank_ami(ami_dict, "../result/skill_graph.txt", 10)
	# test()










