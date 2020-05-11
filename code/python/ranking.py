"""
Given a job list, retrieve its top similar jobs
"""
import numpy as np
import pandas as pd 
import heapq
from collections import defaultdict

from scipy import sparse,spatial
from numpy import linalg as LA

'''load job queries'''
def load_query(job_query_file):
	print("loading query set!")
	query_set = set()
	with open(job_query_file) as f:	
		for line in f:
			query_set.add(line.rstrip())
	return query_set

'''generate query {id:name} dictionary'''	
def load_job_id(query_set, job_id_file):
	print("loading query dictionary!")
	query_dict = {}
	jds = pd.read_csv(job_id_file,usecols=["bgtjobid","cleantitle"]) 
	
	for index, row in jds.iterrows(): 
		for query in query_set:
			if row["cleantitle"] == query:
				query_dict[str(row["bgtjobid"])] = row["cleantitle"]
	return query_dict


'''generate {cid:[jobid...]} and {jobid:cid} dictionary'''
def load_job_community(job_community_file):
	print("loading job community!")
	job_community_dict = dict()
	community_job_dict = defaultdict(list)
	
	with open(job_community_file) as f:	
		for line in f:
			if line.startswith("job"):
				continue
			result = line.rstrip().split(",")
			jobid = result[0]
			cid = result[1]
			job_community_dict[jobid] = cid
			community_job_dict[cid].append(jobid)
	return job_community_dict,community_job_dict

'''generate {jobid:vector} dictionary'''
def load_job_vec(job_index_file, job_vector_file):
	print("loading job vectors!")
	job_vector_l = []
	with open(job_vector_file) as f:	
		for line in f:
			result = line.rstrip().split(",")
			result = [float(v) for v in result]
			job_vector_l.append(result)

	job_vector_dict = dict()	
	with open(job_index_file) as f:	
		for line in f:
			if line.startswith("job"):
				continue
			result = line.rstrip().split(",")
			jobid = result[0]
			index = int(result[1])
			job_vector_dict[jobid] = job_vector_l[index]
	return job_vector_dict

'''given a list of queries, find the top similar jobs in the same community '''
def ranking(query_dict, job_community_dict,community_job_dict, job_vector_dict, query_ranking_file,topK):
	print("retrieve query top ranked jobs!")
	bw = open(query_ranking_file, 'w')
	bw.write("qid,query_name,jobid,ranking,score\n")
	count = 0
	for qid,name in query_dict.items():
		count += 1
		if count %100 == 0:
			print("finished query:", count)

		if qid not in job_community_dict: # current query not in the job list 
			# print(qid,type(qid)," is not in the job list")
			continue 
		query_cid = job_community_dict[qid]
		query_vector = job_vector_dict[qid] 
		same_community_job_l = community_job_dict[query_cid]

		score_l = []
		for jobid in same_community_job_l:
			job_vector = job_vector_dict[jobid] 
			if LA.norm(query_vector) == 0 or LA.norm(job_vector) == 0:
				score = -1.0
			else:
				score = 1 - spatial.distance.cosine(query_vector, job_vector)#cosine similarity(curr_vec, temp_vec)
			if score >= 0 and score <0.99:
				score_l.append([score,jobid])	

		top_jobs = heapq.nlargest(topK, score_l)
		
		ranking = 0
		for [score,jobid] in top_jobs:
			ranking += 1
			bw.write(qid + "," + name + "," + jobid + "," + str(ranking) + "," + str(score) + "\n")

	bw.close()

def check_id_exist(jobid,raw_data_file):
	with open(raw_data_file) as f:	
		for line in f:
			result = line.rstrip().split(",")
			# print(jobid)
			if result[1] == jobid:
				print(jobid)

if __name__ == "__main__": 
	job_query_file = "../data/job_query.txt"
	job_id_file = "../data/job_id.csv"
	job_community_file = "../result/indiana/job_community.txt"#"../result/recommender/job_community_small.txt" #"../result/indiana/job_community.txt"
	job_index_file = "../result/indiana/job_index.txt"#"../result/recommender/job_index_small.txt"#"../result/indiana/job_index.txt"
	job_vector_file = "../result/indiana/job_vector.txt"#"../result/recommender/job_vector_small.txt"#"../result/indiana/job_vector.txt"
	query_ranking_file = "../result/indiana/query_ranking.txt"#"../result/recommender/query_ranking_small.txt"#"../result/indiana/query_ranking.txt"
	
	query_set = load_query(job_query_file)
	query_dict = load_job_id(query_set, job_id_file)
	job_community_dict,community_job_dict = load_job_community(job_community_file)
	job_vector_dict = load_job_vec(job_index_file, job_vector_file)

	ranking(query_dict, job_community_dict, community_job_dict, job_vector_dict, query_ranking_file, 500)

	# jobid = "37835167721"
	# raw_data_file = "/Users/gaozheng/Desktop/skills-count-per-year-totals-wskils-indiana-non-na-2010-2018.csv"

	# check_id_exist(jobid,raw_data_file)











