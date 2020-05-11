"""
This is the code to play with a toy dataset by ranking skills globally and locally in cluster-level.
"""
import pandas as pd 
import numpy as np
from sklearn.preprocessing import Normalizer
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
from collections import defaultdict

from scipy import sparse

"""rank skill scores, output: {skill:score,...}"""
def skill_rank(skill_info_file, skill_rank_file, job_name):
	skill_rank_dict = dict()
	df = pd.read_csv(skill_info_file,sep='|')
	df = df.loc[df["cleantitle"] == job_name]
	skill = df[["skill"]].values.transpose()[0]
	# print(skill,skill.shape)
	weight_mean = df["weight"].replace(0, np.nan).mean(skipna=True)
	df["weight"].replace(0, weight_mean, inplace=True)
	job_count_mean = df["job_count"].mean(skipna=True)
	df["job_count"].replace(np.nan, weight_mean, inplace=True)
	
	df = df[["weight","salary","job_count"]].apply(lambda x: x/100.0).values.transpose()  
	l2 = Normalizer(norm='l2')
	df = l2.fit_transform(df)
	score = df[0]+df[1]+df[2]
	combination = zip(score,skill)
	combination.sort(reverse=True)

	bw = open(skill_rank_file, 'w')
	bw.write("skill|rank|score \n")

	rank = 1
	for (score,skill) in combination: # it contains duplicates
		if skill in skill_rank_dict:
			continue
		skill_rank_dict[skill] = score
		bw.write(skill + "|" + str(rank) + "|" + str(score)+"\n")
		rank += 1
	bw.close()

	return skill_rank_dict


""" cluster skills given relevant jobs, output : {cid:{skill1, skill2},...}"""
def skill_clu(skill_job_file, skill_clu_file):
	# load skill-job graph into sparse matrix
	job_index_dict = dict()
	skill_index_dict = dict()
	row = []
	col = []
	data = []

	with open(skill_job_file) as f:	
		for line in f:
			if line.startswith("skill"):
				continue
			result = line.rstrip().split("|")
			skill = result[0]
			jobid = result[1]

			if skill not in skill_index_dict:
				skill_index_dict[skill] = len(skill_index_dict)
			
			if jobid not in job_index_dict:
				job_index_dict[jobid] = len(job_index_dict)
			
			row.append(skill_index_dict[skill])
			col.append(job_index_dict[jobid])			
			data.append(1)

	matrix = sparse.csr_matrix((data, (row, col)), shape=(len(skill_index_dict), len(job_index_dict)))
		
	# NMF
	model = NMF(n_components=2, init='random', random_state=0)
	skill_vecs = model.fit_transform(matrix)

	# Kmeans
	kmeans = KMeans(n_clusters=10, random_state=0,max_iter=10).fit(skill_vecs)
	labels = kmeans.labels_

	# generate cluster dictionary
	bw = open(skill_clu_file, 'w')
	bw.write("skill|cluster_id \n")

	skill_clu_dict = defaultdict(list) 
	for skill,index in skill_index_dict.items():
		cid = labels[index]
		skill_clu_dict[cid].append(skill)
		bw.write(skill + "|" + str(cid) + "\n")

	return skill_clu_dict
"""rank skill in each cluster"""
def skill_rank_by_clu(skill_rank_dict, skill_clu_dict, skill_rank_by_clu_file):
	bw = open(skill_rank_by_clu_file, 'w')
	bw.write("clusterid|skill|rank|score \n")
	for cid, skill_l in skill_clu_dict.items():
		skill_score_l = []
		for skill in skill_l:
			if skill in skill_rank_dict:
				skill_score_l.append((skill_rank_dict[skill],skill))
		skill_score_l.sort(reverse=True)

		rank = 0
		for (score,skill) in skill_score_l:
			rank += 1
			bw.write(str(cid) + "|" + skill + "|" + str(rank)  + "|" + str(score) + "\n")

	bw.close()

if __name__ == "__main__": 
	#input
	job_name = "Insurance Specialist"
	skill_info_file = "../data/toy_example/skill_info.psv"
	skill_job_file = "../data/toy_example/skill_job.psv"

	#output
	skill_rank_file = "../report/toy_example/" + job_name.replace(" ","-") + "_skill_ranking.csv"
	skill_clu_file = "../report/toy_example/" + job_name.replace(" ","-") + "_skill_cluster.csv"
	skill_rank_by_clu_file = "../report/toy_example/" + job_name.replace(" ","-") + "_skill_ranking_by_cluster.csv"
	skill_rank_dict = skill_rank(skill_info_file, skill_rank_file,job_name)
	skill_clu_dict = skill_clu(skill_job_file, skill_clu_file)
	skill_rank_by_clu(skill_rank_dict, skill_clu_dict, skill_rank_by_clu_file)












