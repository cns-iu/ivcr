"""
Retrieve the top 5/50/500 most similar jobs for 20 pre-selected jobs.
"""
import numpy as np
import pandas as pd 
import heapq
from collections import defaultdict

from scipy import sparse,spatial
from numpy import linalg as LA
import tqdm

'''load query name and id'''
def load_query(job_query_file):
	print("loading query name and id!")
	query_dict = dict()
	with open(job_query_file) as f:	
		for line in f:
			result = line.rstrip().split(",")
			job_name = result[0]
			jobid = result[1]
			query_dict[jobid] = job_name
	return query_dict

'''generate all job {id:name} dictionary'''	
def load_job_id(job_name_file):
	print("loading job name and id!")
	job_dict = {}
	jobs = pd.read_csv(job_name_file,usecols=["bgtjobid","cleantitle"]) 
	
	count = 0
	for index, row in jobs.iterrows(): 
		count += 1
		if count %10000 == 0:
			print("load row count:", count)
		job_dict[str(row["bgtjobid"])] = row["cleantitle"]
	return job_dict

'''generate {jobid:vector} dictionary'''
def load_job_vec(job_index_file, job_vector_file):
	print("loading job vectors!")
	job_vector_l = []
	count = 0
	with open(job_vector_file) as f:	
		for line in f:
			count += 1
			if count %10000 == 0:
				print("load job vector:", count)
			result = line.rstrip().split(",")
			result = [float(v) for v in result]
			job_vector_l.append(result)

	job_vector_dict = dict()	
	count = 0
	with open(job_index_file) as f:	
		for line in f:
			if line.startswith("job"):
				continue
			count += 1
			if count %10000 == 0:
				print("load job index:", count)
				
			result = line.rstrip().split(",")
			jobid = result[0]
			index = int(result[1])
			job_vector_dict[jobid] = job_vector_l[index]
	return job_vector_dict

'''given a list of queries, find the top similar jobs in the same community '''
def ranking(query_dict,job_dict, job_vector_dict):
	print("retrieve query top ranked jobs!")
	count = 0
	for qid,name in query_dict.items():
		count += 1
		print("finished query:", count)

		query_vector = job_vector_dict[qid] 
		score_l = []
		for jobid,job_vector in tqdm.tqdm(job_vector_dict.items()):
			if LA.norm(query_vector) == 0 or LA.norm(job_vector) == 0:
				score = -1.0
			else:
				score = 1 - spatial.distance.cosine(query_vector, job_vector)#cosine similarity(curr_vec, temp_vec)
			if score >= 0 and score <0.99:
				score_l.append([score,jobid])

		top_jobs = heapq.nlargest(500, score_l)
		
		# top 5 ranking list
		query_ranking_file = "../result/indiana/top5/"+qid+".txt"
		bw = open(query_ranking_file, 'w')
		bw.write("qid,query_name,jobid,job_name,ranking,score\n")
		ranking = 0
		for [score,jobid] in top_jobs:
			ranking += 1
			bw.write(qid + "," + name + "," + jobid + "," + job_dict[jobid] + "," + str(ranking) + "," + str(score) + "\n")
			if ranking == 5:
				break
		bw.close()

		# top 50 ranking list
		query_ranking_file = "../result/indiana/top50/"+qid+".txt"
		bw = open(query_ranking_file, 'w')
		bw.write("qid,query_name,jobid,job_name,ranking,score\n")
		ranking = 0
		for [score,jobid] in top_jobs:
			ranking += 1
			bw.write(qid + "," + name + "," + jobid + "," + job_dict[jobid] + "," + str(ranking) + "," + str(score) + "\n")
			if ranking == 50:
				break
		bw.close()

		# top 500 ranking list
		query_ranking_file = "../result/indiana/top500/"+qid+".txt"
		bw = open(query_ranking_file, 'w')
		bw.write("qid,query_name,jobid,job_name,ranking,score\n")
		ranking = 0
		for [score,jobid] in top_jobs:
			ranking += 1
			bw.write(qid + "," + name + "," + jobid + "," + job_dict[jobid] + "," + str(ranking) + "," + str(score) + "\n")
			if ranking == 500:
				break
		bw.close()

if __name__ == "__main__": 
	job_query_file = "../data/job_query_id.txt"
	job_name_file = "../large_data/extract-jobs-by-skill-5more-agg.csv" 
	job_index_file = "../result/indiana/job_index.txt"#"../result/recommender/job_index_small.txt"#"../result/indiana/job_index.txt"
	job_vector_file = "../result/indiana/job_vector.txt"#"../result/recommender/job_vector_small.txt"#"../result/indiana/job_vector.txt"
	
	query_dict = load_query(job_query_file)
	job_dict = load_job_id(job_name_file)
	job_vector_dict = load_job_vec(job_index_file, job_vector_file)

	ranking(query_dict,job_dict, job_vector_dict)








