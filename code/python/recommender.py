"""
Build a recommender system to retrieve the top similar jobs 
""" 
from sklearn.decomposition import NMF

from scipy import sparse,spatial

from tqdm import tqdm, trange
import heapq
from collections import defaultdict
# import pickle
# import pandas as pd 
import numpy as np
import operator
from sklearn.cluster import KMeans
from numpy import linalg as LA

"""check skill count for jobs"""
def skill_count(input_file, output_file):
	skill_count_dict = dict()

	with open(input_file) as f:	
		for line in f:
			if line.startswith("year"):
				continue
			result = line.rstrip().split(",")
			year = result[0]
			jobid = result[1]
			skills = result[2].split("|")
			for skill in skills:
				if skill not in skill_count_dict:
					skill_count_dict[skill] = 0
				skill_count_dict[skill] = skill_count_dict[skill] + 1
	bw = open(output_file, 'w')
	bw.write("skill,count\n")
	for k,v in skill_count_dict.items():
		bw.write(k+","+str(v)+"\n")
	bw.close()

"""generate sparse matrix for job-skill matrix, job is the row; skill is the column"""
def generate_sparse_matrix(input_file,job_index_file,skill_index_file):
	job_index_dict = dict()
	skill_index_dict = dict()
	row = []
	col = []
	data = []
	count = 0
	job_N= 0
	with open(input_file) as f:	
		for line in f:
			if line.startswith("year"):
				continue
			count += 1
			if count %1000 == 0:
				print("current loading jobs:",count)
				# break
			result = line.rstrip().split(",")
			year = result[0]
			job = result[1]
			skills = result[2].split("|")

			if len(skills) >= 5 :
				job_N += 1
				job_index_dict[job] = len(job_index_dict)
				for skill in skills:
					if skill not in skill_index_dict:
						skill_index_dict[skill] = len(skill_index_dict)
					row.append(job_index_dict[job])
					col.append(skill_index_dict[skill])
					data.append(1)
	print("number of jobs:", job_N)
	print("start to construct sparse matrix")
	matrix = sparse.csr_matrix((data, (row, col)), shape=(len(job_index_dict), len(skill_index_dict)))

	print("save index to file")
	bw = open(job_index_file, 'w')
	sorted_job_index = sorted(job_index_dict.items(), key=operator.itemgetter(1))
	bw.write("job,index\n")
	for (job,index) in sorted_job_index:
		bw.write(job+","+str(index)+"\n")
	bw.close()

	bw = open(skill_index_file, 'w')
	bw.write("skill,index\n")
	sorted_skill_index = sorted(skill_index_dict.items(), key=operator.itemgetter(1))
	for (skill,index) in sorted_skill_index:
		bw.write(skill+","+str(index)+"\n")
	bw.close()

	return matrix

""" NMF to generate job & skill low dimensional representation"""
def get_NMF(matrix, job_file, skill_file):
	print("start to run NMF model")
	model = NMF(n_components=50, init='random', random_state=0)

	jobs = model.fit_transform(matrix)
	skills = model.components_.transpose()

	print("save model result to files")
	bw = open(job_file, 'w')
	for job in jobs:
		job = list(job)
		job = ",".join(str(v) for v in job)
		bw.write(job + "\n")
	bw.close()

	bw = open(skill_file, 'w')
	for skill in skills:
		skill = list(skill)
		skill = ",".join(str(v) for v in skill)
		bw.write(skill + "\n")
	bw.close()

"""kmeans clustering"""
def get_kmeans(job_vector_file, job_index_file, job_community_file, cluster_N):
	print("loading job vectors")
	job_vector = []
	with open(job_vector_file) as f:	
		for line in f:
			result = line.rstrip().split(",")
			result = [float(v) for v in result]
			job_vector.append(result)

	print("start Kmeans")
	kmeans = KMeans(n_clusters=cluster_N, random_state=0,max_iter=50).fit(job_vector)
	labels = kmeans.labels_

	bw = open(job_community_file, 'w')
	bw.write("job,community_id\n")
	with open(job_index_file) as f:	
		for line in f:
			if line.startswith("job"):
				continue
			result = line.rstrip().split(",")
			job = result[0]
			index = int(result[1])
			bw.write(job+","+str(labels[index])+"\n")
	bw.close()

def get_ranking_by_kmeans(job_vector_file, job_index_file, job_community_file, job_ranking_file,topK):
	
	# load job vectors to dictionary
	print("loading job vectors")
	job_vector = []
	with open(job_vector_file) as f:	
		for line in f:
			result = line.rstrip().split(",")
			result = [float(v) for v in result]
			job_vector.append(result)

	# load job index to dictionary
	print("loading job index")
	index_dict = dict()
	with open(job_index_file) as f:	
		for line in f:
			if line.startswith("job"):
				continue
			result = line.rstrip().split(",")
			job = result[0]
			index = int(result[1])
			index_dict[job] = index

	# get job ids for each community
	print("loading job ids")
	community_dict = defaultdict(list) 
	with open(job_community_file) as f:	
		for line in f:
			result = line.rstrip().split(",")
			job = result[0]
			cid = result[1] 
			community_dict[cid].append(job)

	# calculate pairwise job similarity in each community
	print("calculate pairwise job similarity")
	similarity_dict = defaultdict(list)
	count = 0
	for cid,jobs in community_dict.items():
		count += 1
		print("current community number:",count)
		for i in trange(len(jobs)-1):
			current_job = jobs[i]
			current_jid = index_dict[current_job]
			current_vec = job_vector[current_jid]
			for j in range(i+1,len(jobs)):
				temp_job = jobs[j]
				temp_jid = index_dict[temp_job]
				temp_vec = job_vector[temp_jid]
				if LA.norm(current_vec) == 0 or LA.norm(temp_vec) == 0:
					score = 0
				else:
					score = 1 - spatial.distance.cosine(current_vec, temp_vec)#cosine similarity(curr_vec, temp_vec)
				
				if score >= 0 and score <0.99: # set critera to throw some too high or low similarity job pairs 
					similarity_dict[current_job].append([score,temp_job]) #store other skills current ami to skill
					similarity_dict[temp_job].append([score,current_job])
	
	# rank each job top similar jobs
	print("rank top jobs")
	bw = open(job_ranking_file, 'w')
	count = 0
	for job, score_l in similarity_dict.items():
		count += 1
		if count %500 == 0:
			print(count)
		top_jobs = heapq.nlargest(topK, score_l)
		for [score,curr_job] in top_jobs:
			bw.write(job + "," + curr_job + "," + str(score) + "\n")
	bw.close()


if __name__ == "__main__": 
	raw_data_file = "../large_data/skills-count-per-year-totals-wskils-indiana-non-na-2010-2018.csv"
	
	job_index_file = "../result/indiana/job_index.txt"
	job_vector_file = "../result/indiana/job_vector.txt"
	job_community_file = "../result/indiana/job_community.txt"
	job_ranking_file = "../result/indiana/job_ranking.txt"
	
	skill_count_file = "../result/indiana/skill_count.csv"
	skill_index_file = "../result/indiana/skill_index.txt"
	skill_vector_file = "../result/indiana/skill_vector.txt"

	cluster_N = 2000 # number of clusters in kmeans
	top_N = 500 # top K most similar jobs for each job

	skill_count(raw_data_file, skill_count_file)

	matrix = generate_sparse_matrix(raw_data_file,\
										job_index_file, \
										skill_index_file)
	get_NMF(matrix, job_vector_file, skill_vector_file)

	get_kmeans(job_vector_file, job_index_file, job_community_file,cluster_N)


	get_ranking_by_kmeans(job_vector_file, job_index_file, job_community_file, job_ranking_file,top_N)
















