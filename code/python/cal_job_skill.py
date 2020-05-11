from collections import defaultdict
import numpy as np
import pandas as pd 
import random
import heapq
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
import operator

from scipy import sparse,spatial
from numpy import linalg as LA
import tqdm

''' only keep jobs with skill number in 10% - 90% '''
def filter_job(job_skill_file):
	job_skill_dict = defaultdict(list) 
	count = 0
	with open(job_skill_file) as f:	
		for line in f:
			count += 1
			if count % 1000 == 0:
				print("current count", count)
				# break
			result = line.rstrip().split(",")
			if line.startswith("BGTJobId"):
				continue
			job_skill_dict[result[0]].append(result[1]) 

	job_count = [len(s) for s in job_skill_dict.values()]
	job_count = np.asarray(job_count)
	job_low = np.percentile(job_count, 10) #-1 #np.percentile(job_count, 10)
	job_high = np.percentile(job_count, 90) #100 #np.percentile(job_count, 90) 

	job_set = set()
	new_job_skill_dict = defaultdict(list)
	skill_job_dict = defaultdict(list)
	for k,v in job_skill_dict.items():
		if len(v) < job_high and len(v) > job_low:
			job_set.add(k)
			new_job_skill_dict[k] = v
			for skill in v:
				skill_job_dict[skill].append(k)

	# print(low,high,len(job_skill_dict),len(job_set))
	return new_job_skill_dict, skill_job_dict, job_set

''' for each skill, calculate the ratio of jobs it contains in each month/year '''
def cal_skill_ratio(skill_job_dict, job_file, skill_year_file, skill_month_file):
	year_count_dict = defaultdict(float)
	month_count_dict = defaultdict(float)
	year = set()
	month = set()
	job_info_dict = defaultdict(list)
	jobs = pd.read_csv(job_file,usecols=["BGTJobId","JobDate"]) 
	count = 0
	for index, row in jobs.iterrows(): 
		count += 1
		if count %10000 == 0:
			print("load job count:", count)
		id = str(row["BGTJobId"])
		date = str(row["JobDate"])
		curr_year = date.split("-")[0]
		curr_month = curr_year + "-" + date.split("-")[1]
		year.add(curr_year)
		month.add(curr_month)
		year_count_dict[curr_year] = year_count_dict[curr_year] + 1.0
		month_count_dict[curr_month] = month_count_dict[curr_month] + 1.0
		job_info_dict[id] = [curr_year, curr_month]
	year = list(year)
	year.sort()
	month = list(month)
	month.sort()


	bw1 = open(skill_year_file, 'w')
	bw1.write("SkillId," + ",".join(year) + "\n")

	bw2 = open(skill_month_file, 'w')
	bw2.write("SkillId," + ",".join(month) + "\n")

	count = 0
	for skill,job_l in skill_job_dict.items():
		count += 1
		if count %1000 == 0:
			print("load skill count:", count)

		skill_year = defaultdict(float)
		skill_month = defaultdict(float)
		for job in job_l:
			job_year = job_info_dict[job][0]
			job_month = job_info_dict[job][1]
			skill_year[job_year] = skill_year[job_year] + 1.0/year_count_dict[job_year]
			skill_month[job_month] = skill_month[job_month] + 1.0/month_count_dict[job_month]
		year_dist = []
		month_dist = []

		for y in year:
			if y in skill_year:
				year_dist.append(str(round(skill_year[y], 4)))
			else:
				year_dist.append("0")

		for m in month:
			if m in skill_month:
				month_dist.append(str(round(skill_month[m], 4)))
			else:
				month_dist.append("0")

		bw1.write(skill + "," + ",".join(year_dist) + "\n")
		bw2.write(skill + "," + ",".join(month_dist) + "\n")

	bw1.close()
	bw2.close()


''' calculate skill count distribution over years/months '''
def cal_skill_dist(skill_job_dict, job_file, skill_year_file, skill_month_file):
	year = set()
	month = set()
	job_info_dict = defaultdict(list)
	jobs = pd.read_csv(job_file,usecols=["BGTJobId","JobDate"]) 
	count = 0
	for index, row in jobs.iterrows(): 
		count += 1
		if count %10000 == 0:
			print("load job count:", count)
		id = str(row["BGTJobId"])
		date = str(row["JobDate"])
		curr_year = date.split("-")[0]
		curr_month = date.split("-")[1]
		year.add(curr_year)
		month.add(curr_year+"-"+curr_month)
		job_info_dict[id] = [curr_year, curr_year+"-"+curr_month]
	year = list(year)
	year.sort()
	month = list(month)
	month.sort()

	bw1 = open(skill_year_file, 'w')
	bw1.write("SkillId," + ",".join(year) + "\n")

	bw2 = open(skill_month_file, 'w')
	bw2.write("SkillId," + ",".join(month) + "\n")

	count = 0
	for skill,job_l in skill_job_dict.items():
		count += 1
		if count %1000 == 0:
			print("load skill count:", count)

		skill_year = defaultdict(float)
		skill_month = defaultdict(float)
		for job in job_l:
			job_year = job_info_dict[job][0]
			job_month = job_info_dict[job][1]
			skill_year[job_year] = skill_year[job_year] + 1.0/len(job_l)
			skill_month[job_month] = skill_month[job_month] + 1.0/len(job_l)
		year_dist = []
		month_dist = []

		for y in year:
			if y in skill_year:
				year_dist.append(str(round(skill_year[y], 2)))
			else:
				year_dist.append("0")

		for m in month:
			if m in skill_month:
				month_dist.append(str(round(skill_month[m], 2)))
			else:
				month_dist.append("0")

		bw1.write(skill + "," + ",".join(year_dist) + "\n")
		bw2.write(skill + "," + ",".join(month_dist) + "\n")

	bw1.close()
	bw2.close()

''' random select K jobs '''
def random_job_query(job_set, K):
	job_query_l = np.random.choice(list(job_set), K, replace=False)
	return job_query_l

''' get job titles, stored in dictoionary {id:title} '''
def get_job_info(job_set, job_file):
	job_info_dict = dict()

	jobs = pd.read_csv(job_file,usecols=["BGTJobId","Title"]) 
	count = 0
	for index, row in jobs.iterrows(): 
		count += 1
		if count %10000 == 0:
			print("load job count:", count)
		id = str(row["BGTJobId"])
		title = "\"" + str(row["Title"]) + "\""
		if id in job_set:
			job_info_dict[id] = title
	return job_info_dict

def get_job_skill_matrix(job_skill_dict):
	print("generate job-skill matrix!")
	job_index_dict = dict()
	reverse_job_index_dict = dict()
	skill_index_dict = dict()
	row = []
	col = []
	data = []

	for jobid,skills in job_skill_dict.items():
		if jobid not in job_index_dict:
			job_index_dict[jobid] = len(job_index_dict)
			reverse_job_index_dict[len(reverse_job_index_dict)] = jobid

		for skill in skills:
			if skill not in skill_index_dict:
				skill_index_dict[skill] = len(skill_index_dict)
			
			row.append(job_index_dict[jobid])						
			col.append(skill_index_dict[skill])
			data.append(1.0)

	matrix = sparse.csr_matrix((data, (row, col)), shape=(len(job_index_dict), len(skill_index_dict)))
	
	return job_index_dict, skill_index_dict, reverse_job_index_dict, matrix	

''' use NMF to calculate job vector '''
def get_job_vector(matrix, K):
	print("calculating job vectors!")
	
	# NMF
	model = NMF(n_components=K, init='random', random_state=0)
	job_vecs = model.fit_transform(matrix)
	return job_vecs

''' use Kmeans on job vectors to get job cluster '''
def get_job_cluster(job_vecs, K):
	print("calculating job clusters!")
	# Kmeans
	kmeans = KMeans(n_clusters=K, random_state=0,max_iter=10).fit(job_vecs)
	job_cluster = kmeans.labels_
	cluster_job_dict = defaultdict(list)

	for i in range(len(job_cluster)):
		cluster_job_dict[job_cluster[i]].append(i)
	return job_cluster, cluster_job_dict

def get_skill_risk_score(skill_risk_file):
	skill_risk_dict = defaultdict(float)
	skills = pd.read_csv(skill_risk_file,usecols=["SkillId","risk"])  
	for index, row in skills.iterrows():  
		skill_id = str(row["SkillId"])
		skill_risk = float(row["risk"])/100.0
		skill_risk_dict[skill_id] = skill_risk
	return skill_risk_dict

''' given a set of job queries, generate their top 5/50/500 similar jobs and stores 
into individual file per job. job ranking is calculated for the jobs in the same cluster.
And return top k relevant skills for each job, using userKNN model '''
def get_top_similar_jobs(job_skill_dict, job_query_l, job_cluster, cluster_job_dict, \
						job_index_dict, reverse_job_index_dict, job_vecs, job_info_dict, \
						skill_risk_dict, output_folder, K):
	print("retrieve query top ranked jobs!")
	count = 0
	for job_query in job_query_l:
		count += 1
		print("finished query:", count)

		job_title = job_info_dict[job_query]
		job_index = job_index_dict[job_query]
		job_vec = job_vecs[job_index]
		job_cid = job_cluster[job_index]
		jobs_in_same_cluster = cluster_job_dict[job_cid]

		score_l = []
		for j_index in jobs_in_same_cluster:
			j_id = reverse_job_index_dict[j_index]

			if j_index == job_index: # remove the current job
				continue

			j_vec = job_vecs[j_index]
			if LA.norm(job_vec) == 0 or LA.norm(j_vec) == 0:
				score = -1.0
			else:
				score = 1 - spatial.distance.cosine(job_vec, j_vec)#cosine similarity(curr_vec, temp_vec)
			if score >= 0 and score <0.99:
				score_l.append([score,j_id])

		top_jobs = heapq.nlargest(500, score_l)

		"""
		top relevant skills 
		"""
		query_ranking_file = output_folder + "/skill_ranking/" + job_query + ".txt"
		bw = open(query_ranking_file, 'w')
		bw.write("jobid,job_title,skill_id,ranking,score\n")

		skills_score_dict = defaultdict(float)
		job_skills = job_skill_dict[job_query]
		
		for skill in job_skills:
			skills_score_dict[skill] = skills_score_dict[skill] + 1.0

		ranking = 0
		for [score,jobid] in top_jobs:
			if ranking == 500:
				break
			ranking += 1
			j_skills = job_skill_dict[jobid]
			for skill in j_skills:
				skills_score_dict[skill] = skills_score_dict[skill] + score
		
		max_score = max(skills_score_dict.values()) 
		for k,v in skills_score_dict.items():
			skills_score_dict[k] = v/max_score + 1.5 * skill_risk_dict[k]

		sorted_skills = sorted(skills_score_dict.items(), key=lambda kv: kv[1], reverse=True)

		for i in range(min(len(sorted_skills),K)):
			(skill, score) = sorted_skills[i]
			bw.write(job_query + "," + job_title + "," + skill + "," + str(i+1) + "," + str(score) + "\n")
			
		bw.close()



		"""
		top similar jobs 
		"""
		# top 5 ranking list
		query_ranking_file = output_folder + "/top5/" + job_query + ".txt"
		bw = open(query_ranking_file, 'w')
		bw.write("qid,query_name,jobid,job_name,ranking,score\n")
		ranking = 0
		for [score,jobid] in top_jobs:
			if ranking == 5:
				break
			bw.write(job_query + "," + job_title + "," + jobid + "," + job_info_dict[jobid] + "," + str(ranking) + "," + str(score) + "\n")
			ranking += 1
			
		bw.close()

		# top 50 ranking list
		query_ranking_file = output_folder + "/top50/" + job_query + ".txt"
		bw = open(query_ranking_file, 'w')
		bw.write("qid,query_name,jobid,job_name,ranking,score\n")
		ranking = 0
		for [score,jobid] in top_jobs:
			if ranking == 50:
				break
			bw.write(job_query + "," + job_title + "," + jobid + "," + job_info_dict[jobid] + "," + str(ranking) + "," + str(score) + "\n")
			ranking += 1
			
		bw.close()

		# top 500 ranking list
		query_ranking_file = output_folder + "/top500/" + job_query + ".txt"
		bw = open(query_ranking_file, 'w')
		bw.write("qid,query_name,jobid,job_name,ranking,score\n")
		ranking = 0
		for [score,jobid] in top_jobs:
			if ranking == 500:
				break
			bw.write(job_query + "," + job_title + "," + jobid + "," + job_info_dict[jobid] + "," + str(ranking) + "," + str(score) + "\n")
			ranking += 1
			
		bw.close()


	

if __name__ == "__main__": 
	job_skill_file = "../large_data/job_skill/job_skill_relationships.csv" #"../data/test/job_skill_relationships.csv" # "../large_data/job_skill/job_skill_relationships.csv"
	job_file = "../large_data/job_skill/jobs.csv" #"../data/test/jobs.csv" # "../large_data/job_skill/jobs.csv"
	skill_file = "../large_data/job_skill/skills.csv" #"../data/test/skills.csv" # "../large_data/job_skill/skills.csv"
	skill_year_file = "../report/skill_dist/skill_year_dist.csv"
	skill_month_file = "../report/skill_dist/skill_month_dist.csv"
	skill_risk_file = "../large_data/job_skill/skill_risk.csv"

	skill_risk_dict = get_skill_risk_score(skill_risk_file)
	job_skill_dict, skill_job_dict, job_set = filter_job(job_skill_file)

	### calculate skill distribution ### 
	# cal_skill_dist(skill_job_dict, job_file, skill_year_file, skill_month_file)
	# cal_skill_ratio(skill_job_dict, job_file, skill_year_file, skill_month_file)

	### calculate job top similar job/skill ranking list
	job_query_l = random_job_query(job_set, 500)
	job_info_dict = get_job_info(job_set, job_file)
	job_index_dict, skill_index_dict, reverse_job_index_dict, matrix = get_job_skill_matrix(job_skill_dict)
	job_vecs = get_job_vector(matrix, 10)
	job_cluster, cluster_job_dict = get_job_cluster(job_vecs, 1000) 

	output_folder = "../report/skill_dist"
	get_top_similar_jobs(job_skill_dict, job_query_l, job_cluster, cluster_job_dict,  \
						job_index_dict, reverse_job_index_dict, job_vecs, job_info_dict, \
						skill_risk_dict , output_folder, 100)

