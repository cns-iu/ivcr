import numpy as np
from sklearn.decomposition import NMF
from scipy import sparse
from sklearn.cluster import KMeans
def get_kmeans_dist(job_community_file):
	community_count_dict = dict()
	with open(job_community_file) as f:	
		for line in f:
			result = line.rstrip().split(",")
			cid = result[1]
			if cid not in community_count_dict:
				community_count_dict[cid] = 0
			community_count_dict[cid] = community_count_dict[cid] + 1
	print(community_count_dict)
def test():
	""" Create sparse data """
	# nnz_i, nnz_j, nnz_val = np.random.choice(531, size=45), \
	#                         np.random.choice(315, size=45), \
	#                         np.random.random(size=45)
	# X =  sparse.csr_matrix((nnz_val, (nnz_i, nnz_j)), shape=(531, 315))
	# print('X-shape: ', X.shape, ' X nnzs: ', X.nnz)
	# print('type(X): ', type(X))
	# # <class 'scipy.sparse.csr.csr_matrix'> #                          !!!!!!!!!!

	# """ NMF """
	# model = NMF(n_components=2, init='random', random_state=0)

	# start_time = pc()
	# W = model.fit_transform(X)
	# end_time = pc()

	# print('Used (secs): ', end_time - start_time)
	# print(model.reconstruction_err_)
	# print(model.n_iter_)
	X = [[1, 1], [2, 1], [3, 1.2], [4, 1], [5, 0.8], [6, 1]]
	kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
	print(kmeans.labels_)

if __name__ == "__main__": 
	# skill_count("../data/skills-count-per-year-totals-wskils-dsde-agg-2010-2018.csv", "../result/skill_count_large.csv")

	# matrix = generate_sparse_matrix("../data/skills-count-per-year-totals-wskils-dsde-agg-2010-2018.csv",\
	# 									"../result/recommender/job_index_small.txt", \
	# 									"../result/recommender/skill_index_small.txt")
	# NMF(matrix, "../result/recommender/job_vector_small.txt", "../result/recommender/skill_vector_small.txt")

	test()
	get_kmeans_dist("../result/recommender/job_community_small.txt")


