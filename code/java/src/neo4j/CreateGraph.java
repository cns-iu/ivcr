/*
It is the main code to generate the Neo4j graph.
*/
package neo4j;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
 

import java.util.Map;

import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Relationship;
import org.neo4j.graphdb.Transaction;

import neo4j.Cypher;

public class CreateGraph {
	
	public static void main(String[] args) throws IOException{
		// TODO Auto-generated method stub
		CreateGraph cg = new CreateGraph();
		System.out.println("Start loading node!");
		HashMap<String,String> nodeMap = cg.loadNodes("../data/skill_count_by_year.csv");
		System.out.println("Start loading edges!");
		ArrayList<String[]> edgeList = cg.loaEdges("../result/skill_graph.txt");
		System.out.println("Node size:"+nodeMap.size()+", edge size:"+edgeList.size());
		System.out.println("start generating the graph!");
		cg.generateGraph(nodeMap, edgeList, "../data/graph.db");
		
	}
	
	/*
	 * load skill graph nodes
	 */
	public HashMap loadNodes(String nodeFile) throws IOException{
		HashMap<String,String> nodeMap = new HashMap<String,String>();
		BufferedReader br = new BufferedReader(new InputStreamReader(
    			new FileInputStream(nodeFile))); 
    	String line = null; 
    	while ((line = br.readLine()) != null) { 
    		String[] content = line.split(",");
    		String skill = content[0];
    		nodeMap.put(skill, line);
    	} 
		return nodeMap;
	}
	
	/*
	 * load skill graph edges
	 */
	public ArrayList<String[]> loaEdges(String edgeFile) throws IOException{
		ArrayList<String[]> edgeList = new ArrayList<String[]>();
		BufferedReader br = new BufferedReader(new InputStreamReader(
    			new FileInputStream(edgeFile))); 
    	String line = null; 
    	while ((line = br.readLine()) != null) { 
    		String[] content = line.split(",");
    		edgeList.add(content);
    	} 
		return edgeList;
	}
	
	/*
	 * generate graph based on node properties and edges
	 */
	public void generateGraph(HashMap<String,String> nodeMap, ArrayList<String[]> edgeList, String dbFolder){
		Cypher cy = new Cypher(dbFolder);
		GraphDatabaseService db = cy.graphDb;
		try ( Transaction tx = db.beginTx()){
			//create all nodes in graph
			int count = 0;
			for (Map.Entry<String,String> entry : nodeMap.entrySet()){
				count += 1;
				if(count % 500 == 0){
					System.out.println("loading node  number:"+count);
				}
					
				cy.addNode("skill", entry.getKey(), entry.getValue());
			}
			//create all edges in graph
			count = 0;
			for (String[] edge : edgeList){
				Node beginNode = cy.checkNode("skill", edge[0], "");
				Node endNode = cy.checkNode("skill", edge[1], "");
				float weight = Float.parseFloat(edge[2]);
				cy.addRelationship(beginNode, endNode, weight);
				count += 1;
				if(count % 500 == 0){
					System.out.println("loading edge number:"+count);
				}
			}
			tx.success();
		}
		
		db.shutdown();
	}
}
