/*
It offers functions to add/check graph node/link in the Neo4j database.
*/
package neo4j;

import java.io.File;

import org.apache.commons.lang.enums.Enum;
import org.neo4j.graphdb.DynamicLabel;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Label;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Relationship;
import org.neo4j.graphdb.RelationshipType;
import org.neo4j.graphdb.Transaction;
import org.neo4j.graphdb.factory.GraphDatabaseFactory;
import org.neo4j.graphdb.index.Index;
import org.neo4j.graphdb.index.IndexHits;
import org.neo4j.graphdb.index.RelationshipIndex;

public class Cypher {
	public Transaction tx;
	public GraphDatabaseService graphDb;
	public Cypher(String db_path) {
		// TODO Auto-generated constructor stub
		this.graphDb = new GraphDatabaseFactory().newEmbeddedDatabase(new File(db_path));
		registerShutdownHook(graphDb);
	}
	
	public static void main(String[] args) {
		// TODO Auto-generated method stub
//		Cypher cy = new Cypher("/Users/gaozheng/Downloads/neo4j-community-3.5.14/data/databases/graph.db");
		Cypher cy = new Cypher("../data/graph.db2");
		GraphDatabaseService db = cy.graphDb;
		try ( Transaction tx = db.beginTx()){
			Node firstNode = db.createNode();
			firstNode.setProperty( "message", "Hello, " );
			Node secondNode = db.createNode();
			secondNode.setProperty( "message", "World!" );
			Relationship relationship = firstNode.createRelationshipTo( secondNode, RelTypes.MUTUAL_INFO );
			relationship.setProperty( "message", "brave Neo4j" );
			tx.success();
		}
		
		db.shutdown();
	}
	private enum RelTypes implements RelationshipType{
		MUTUAL_INFO
	}
	/**
	 * 
	 * add different types of node in graphDB
	 * @param label
	 * @param property
	 */
	 
	public void addNode(String label, String name, String property){
		Label myLabel = Label.label(label); 
		Node myNode = graphDb.createNode(myLabel); 
		myNode.setProperty("name", name);
		myNode.setProperty("year", property);
		Index<Node> userIndex = graphDb.index().forNodes(label);
		userIndex.add(myNode,"name", name);
	}
	
	/**
	 * check whether node exists in DB, if yes, return the node, if no, create a new node and return
	 * @param label
	 * @param property
	 * @return
	 */
	public Node checkNode(String label, String name, String property){ 
		//don't know whether here consuming time
		Index<Node> userIndex = graphDb.index().forNodes(label);
		IndexHits<Node> userNodes = userIndex.get("name", name); 
		Node userNode;
		if(!userNodes.hasNext()){
		    //Create new User node 
			Label myLabel = Label.label(label); 
			Node myNode = graphDb.createNode(myLabel); 
			myNode.setProperty("name", name);
			myNode.setProperty("year", property); 
			userIndex.add(myNode,"name", name);
		
			return myNode;
		} else {  
			return userNodes.next(); 
		} 
	}
	
	
	/**
	 * add a new relationship 
	 * @param beginNode
	 * @param endNode
	 * @param weight
	 * @param relationshipType
	 */
	public void addRelationship(Node beginNode, Node endNode, float weight){
		RelationshipType rt = RelTypes.MUTUAL_INFO;
		Relationship rs = beginNode.createRelationshipTo(endNode,rt);
		rs.setProperty("weight", weight);
		rs.setProperty("name", "MUTUAL_INFO");
		RelationshipIndex rsi = graphDb.index().forRelationships("MUTUAL_INFO");
		rsi.add(rs, "name", "MUTUAL_INFO"); 
	}
	
	/**
	 * if it already has the same relationship between the two node, set the weight+1; 
	 * if not, create a new relationship between the two nodes
	 * @param beginNode
	 * @param endNode
	 * @param relationshipType
	 */
	public Relationship checkRelationship(Node beginNode, Node endNode, float weight){
		RelationshipType rt = RelTypes.MUTUAL_INFO; 
		
		RelationshipIndex rsi = graphDb.index().forRelationships("MUTUAL_INFO");
		IndexHits<Relationship> reevesAsNeoHits = rsi.get("name", "MUTUAL_INFO", beginNode, endNode);
		if(!reevesAsNeoHits.hasNext()){
			Relationship rs = beginNode.createRelationshipTo(endNode,rt);
	    	   rs.setProperty("weight", weight);
	    	   rs.setProperty("name", "MUTUAL_INFO");
	    	   rsi.add(rs, "name", "MUTUAL_INFO");
	    	   return rs;
		}else{
			Relationship rs = reevesAsNeoHits.next(); 
			return rs;
			
		}
	}
	/*
	 * save shut down the graph database
	 */
	private static void registerShutdownHook(final GraphDatabaseService graphDb){
		Runtime.getRuntime().getRuntime().addShutdownHook(new Thread(){
			public void run(){
				graphDb.shutdown();
			}
		});
	}
}
