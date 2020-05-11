# CNS2019: 2019-2020 Winter Break Work for CNS
This project contains the codes and results to build up the skill graph.
**Neo4j manual (need to use Neo4j Java Developer version):**
1. https://neo4j.com/docs/
2. https://neo4j.com/developer/java/
3. https://neo4j.com/docs/java-reference/current/ 

**To visualize graphdb in browser:**
1. download the Neo4j community version, put the generated graphDb under the data/databases/.
2. go to ./bin run <code>bin/neo4j start</code> to start. <code>bin/neo4j stop</code> to stop. 
3. Then visit http://localhost:7474/ to check the visualization. If has authetification issue, set the conf/neo4j.conf as <code>dbms.security.auth_enabled=false</code>. Reference: https://blog.csdn.net/weixin_39198406/article/details/85068102

**Graph construction steps:**

Codes corresponding to all the steps are at <code>./python/process.py</code>.
1. We only select skills appeared in <code>./data/cooccur.csv</code>.
2. For those skills, we calculate their normalized vector representation within the year 2010-2019 from <code>./data/skill_count_by_year.csv</code>..
3. For each skill, we calculate the top 10 other skills with the highest adjusted mutual information in their vectors. 
4. Given a skill, it will add a link to its top 10 most similar skills, which forms a graph stored in <code>./result/skill_graph.txt</code>. The edge weight is the corresponding adjusted mutual information score.

**Store graph in Neo4j:**

Codes corresponding to all the steps are at <code>./java/*</code>.
1. The code in <code>./java/\*</code> is a whole project and needs to be imported to Eclipse. <code>./java/lib/*</code> contains all the required Neo4j dependencies, which needs to be imported as dependencies in the Eclipse project. 
2. The main Java codes are in <code>./java/src/neo4j/*</code>. <code>CreateGraph.java</code> is the main Java to store the graph in Neo4j database. <code>Cypher.java</code> offers the functions to add/check the node/link in a graph.
3. The Neo4j Graph is finally stored at <code>./data/graph.db</code>.

**Skill Trend Detection:**

All skills are associated with monthly appearance count. I use four types of forcasting models to predict its trend, including AR, MA, Simple Smoothing, Exponential Smoothing.
1. Skill monthly count is normalized using L1 norm.
2. <code>statsmodels</code> package is required to install in advance.
3. Run the following command to retrieve trend results (stored at folder ./result/trend/). You can tailor the model and topK retrieved skills within the <code>./python/forcasting.py</code>
```
python forcasting.py
```


**Toy Example - Skill Ranking**

Date: 03/27/2020

Task description:

`data/toy_example/skill_info.psv` stores three jobs and their related skills' information. `data/toy_example/skill_job.psv` stores the same skills' connections with other jobs. There are two tasks to finish. 
1. We aim to rank these skills in `data/toy_example/skill_info.psv` given weight, salary and job_count information.
2. We cluster skills given skill-job connections in `data/toy_example/skill_job.psv` and generate cluster-level skill rankings. 

Steps:
1. For `data/toy_example/skill_info.psv`, we use L2 normalization in skill weight, salary and job_count to calculate the normalized values for the three features. for the cases where weight = 0 or job_count = nan, we use their mean value to substitute.
2. The skill scores are calculated as the sum of weight, salary and job_count. The ranking result is stored at `report/toy_example/skill_ranking.psv`.
3. Skill clusters are calculated using NMF + Kmeans. We first construct a skill-job matrix using their connections showed in `data/toy_example/skill_job.psv`. NMF helps to calculated 10-d vectors for skills. And Kmeans subsquently uses the vectors to generate 10 skill clusters, which is stored at `report/toy_example/skill_cluster.psv`
4. In each cluster, skills are ranked by the scores calculated in Task 1. The output file is stored as `report/toy_example/skill_ranking_by_cluster.psv`.

Findings:
1. The skill cluster sizes are very biased. Few clusters are super large. i.e. cluster 0 contains over 75% skills in its cluster.

**Skill Distribution**

Date: 04/10/2020

Task description:
1. First I calculate the number of total distinct jobs appeared in each month/year. For each skill, I calculate the ratio of jobs that mention it per month/year and stored in a csv file.
2. Generate top 5/50/500 similar jobs for a set of seed jobs. 
    1. Given job-skill relationship file, remove the jobs whose appearance number is in the top 10% or bottom 10% times of all jobs. random sample 500 seed jobs from remaining jobs.
    2. Based on job-skill relationship matrix, use NMF method to learn a 100d representation for each job.
    3. Use Kmeans method on job vector representations to group them in 1000 clusters.
    4. For each of 500 seed jobs, in its clusters, rank top 5/50/500 most simiar jobs using cosine similarity and store the result in individual files per job. 
3. Generate top 100 most relevant skills for a set of seed jobs using UserKNN method.
    1. Based on the previous result in Task 2, I still use the same 500 seed jobs and their vector representations.
    2. For each job, I retrieve its top 500 most similar jobs from results in Task 2, their cosine similarity scores are also recorded.
    3. The risk score of each skill can be retrieved through external file.
    4. The relevance score score(s,i) of each skill s towards current seed job iis calculated as:
    <img src="img/formula.png">
    where J is the 500 most similar jobs. For each job j in the 500 jobs J, we calculate its cosine similarity score towards i as cos(i,j). I(s,j) is a binary function to indicate whether job j requires skill s in their relationships. 
    5. We rank the top 100 skills with highest relevance score.



