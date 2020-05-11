//package test;
//
//import java.io.File;
//import java.io.IOException;
//import java.util.Map;
//import java.util.Map.Entry;
//
//import org.apache.commons.lang.enums.Enum;
//import org.neo4j.graphdb.Direction;
//import org.neo4j.graphdb.DynamicLabel;
//import org.neo4j.graphdb.GraphDatabaseService;
//import org.neo4j.graphdb.Label;
//import org.neo4j.graphdb.Node;
//import org.neo4j.graphdb.Relationship;
//import org.neo4j.graphdb.RelationshipType;
//import org.neo4j.graphdb.Result;
//import org.neo4j.graphdb.Transaction;
//import org.neo4j.graphdb.factory.GraphDatabaseFactory;
//import org.neo4j.graphdb.index.Index;
//import org.neo4j.graphdb.index.IndexHits;
//import org.neo4j.graphdb.index.IndexManager;
//import org.neo4j.graphdb.index.RelationshipIndex;
//
//public class Cypher {
//	public Transaction transaction;
//	private GraphDatabaseService graphDb;
//	public Cypher(File db_path) {
//		// TODO Auto-generated constructor stub
//		this.graphDb = new GraphDatabaseFactory().newEmbeddedDatabase(db_path);
//		registerShutdownHook(graphDb);
//	}
//
//	public static void main(String []args) throws IOException{
////		Cypher cy = new Cypher("/Users/gaozheng/Documents/neo4j-community-2.2.4/data/graph.db");
//////		cy.runQuery("MATCH (n:twitter_hashtag) RETURN n.id");
//////		System.out.println(cy.runQuery("MATCH (n:twitter_hashtag) RETURN n.id"));
////		
////		cy.beginTransaction(); 
//////		Node node1 = cy.checkNode("user", "zheng");
//////		Node node2 = cy.checkNode("user", "zheng");
//////		Node node3 = cy.checkNode("user", "zhengtai"); 
//////		System.out.println(cy.checkNode("user", "zhengtai").getProperty("name"));
//////		System.out.println(cy.checkRelationship(node3, node1, "HASHTAG").getProperty("weight"));
//////		System.out.println(cy.checkRelationship(node3, node1, "RETWEET").getProperty("weight"));
////		
////		cy.getSubGraph("RETWEET");
////		cy.successTransaction();
////		cy.finishTransaction();
////		cy.shutDown();
//		GraphDatabaseService db = new GraphDatabaseFactory().newEmbeddedDatabase("graph.db");
////		try ( Transaction tx = db.beginTx())
////		{
////		    Node myNode = db.createNode();
////		    myNode.setProperty( "user", "my node" );
////		    tx.success();
////		}
//		try ( Transaction ignored = db.beginTx();Result result = db.execute( "match (n {name: ''}) return n, n.name" ) )
//			     
//			{
//			String rows = "";
//			    while ( result.hasNext() )
//			    {
//			        Map<String,Object> row = result.next();
//			        for ( Entry<String, Object> column : row.entrySet() )
//			        {
//			            rows += column.getKey() + ": " + column.getValue() + "; ";
//			        }
//			        rows += "\n";
//			    }
//			System.out.println(rows);
//			}
//			
//	} 
//	/**
//	 * begin transaction
//	 */
//	public void beginTransaction(){
//		this.transaction = graphDb.beginTx();
//	}
//	
//	/**
//	 * success transaction
//	 */
//	public void successTransaction(){
//		this.transaction.success();
//	}
//	
//	/**
//	 * finish transaction
//	 */
//	public void finishTransaction(){
//		this.transaction.close();
//	}
///**
// * run query in neo4j through java, return the result as a stringbuilder,
// * the result may be null at this point
// * @param query
// * @param file_path
// * @return StringBuilder result
// * @throws IOException 
// */
//	public StringBuilder runQuery(String query) throws IOException{ 
//		StringBuilder content =new StringBuilder();
//		Result result = graphDb.execute(query);
//		
//		while (result.hasNext()){		
//	         Map<String, Object> row = result.next();
//	         for (String key : result.columns())
//	         {
//	        	 content.append(row.get(key));
//	        	 content.append("\n");
//	        	 String a = row.get(key).toString();
//	             System.out.printf( "%s = %s%n", key,row.get(key));
//	             
//	         }
//	     }  
//		return content;
//	}
//	
//	/**
//	 * 
//	 * add different types of node in graphDB
//	 * @param label
//	 * @param property
//	 */
//	 
//	public void addNode(String label, String property){
//		
//		Node myNode = graphDb.createNode();
//		Label myLabel = DynamicLabel.label(label); 
//		myNode.addLabel(myLabel);
//		myNode.setProperty("name", property);
//		Index<Node> userIndex = graphDb.index().forNodes(label);
//		userIndex.add(myNode,"name", property);
//	}
//	
//	/**
//	 * check whether node exists in DB, if yes, return the node, if no, create a new node and return
//	 * @param label
//	 * @param property
//	 * @return
//	 */
//	public Node checkNode(String label, String property){ 
//		//don't know whether here consuming time
//		Index<Node> userIndex = graphDb.index().forNodes(label);
//		
//		IndexHits<Node> userNodes = userIndex.get("name", property); 
//		 Node userNode;
//		if(!userNodes.hasNext()){
//		    //Create new User node 
//			userNode = graphDb.createNode();
//			Label myLabel = DynamicLabel.label(label); 
//			userNode.addLabel(myLabel);
//			userNode.setProperty("name", property);
//			userIndex.add(userNode,"name", property);
//		
//			return userNode;
//		} else {  
//			return userNodes.next(); 
//		} 
//	}
//	
//	private static Enum RelTypes implements RelationshipType
//	{
//	    RETWEET,MENTION,REPLY,HASHTAG
//	}
//	
//	/**
//	 * add a new relationship 
//	 * @param beginNode
//	 * @param endNode
//	 * @param weight
//	 * @param relationshipType
//	 */
//	public void addRelationship(Node beginNode, Node endNode, int weight, String relationshipType){
//		RelationshipType rt;
//		if (relationshipType == "RETWEET"){
//			rt = RelTypes.RETWEET;
//		}else if (relationshipType == "MENTION"){
//			rt = RelTypes.MENTION;
//		}else if (relationshipType == "HASHTAG"){
//			rt = RelTypes.HASHTAG;
//		}else {
//			rt = RelTypes.REPLY;
//		}
//		Relationship rs = beginNode.createRelationshipTo(endNode,rt);
//		rs.setProperty("weight", 1);
//		rs.setProperty("name", relationshipType);
//		RelationshipIndex rsi = graphDb.index().forRelationships(relationshipType);
//		rsi.add(rs, "name", relationshipType);
//		
//		
//	}
//	
//	/**
//	 * if it already has the same relationship between the two node, set the weight+1; 
//	 * if not, create a new relationship between the two nodes
//	 * @param beginNode
//	 * @param endNode
//	 * @param relationshipType
//	 */
//	public Relationship checkRelationship(Node beginNode, Node endNode, String relationshipType){
//		RelationshipType rt;
//		if (relationshipType == "RETWEET"){
//			rt = RelTypes.RETWEET;
//		}else if (relationshipType == "MENTION"){
//			rt = RelTypes.MENTION;
//		}else if (relationshipType == "HASHTAG"){
//			rt = RelTypes.HASHTAG;
//		}else {
//			rt = RelTypes.REPLY;
//		}
//		
//		RelationshipIndex rsi = graphDb.index().forRelationships(relationshipType);
//		IndexHits<Relationship> reevesAsNeoHits = rsi.get("name", relationshipType, beginNode, endNode);
//		if(!reevesAsNeoHits.hasNext()){
//			Relationship rs = beginNode.createRelationshipTo(endNode,rt);
//	    	   rs.setProperty("weight", 1);
//	    	   rs.setProperty("name", relationshipType);
//	    	   rsi.add(rs, "name", relationshipType);
//	    	   return rs;
//		}else{
//			Relationship rs = reevesAsNeoHits.next();
//			int weight = (Integer)rs.getProperty("weight");
//			rs.setProperty("weight", weight + 1);
//			return rs;
//			
//		}
//	}
//	
//	
//	public void getSubGraph(String relationshipType){ 
//		//eg: Hashtag:"MATCH (node1)-[r:HASHTAG]->(node2) RETURN node1,node2,r"
//		String query = "MATCH (node1)-[r:"+relationshipType+"]->(node2) RETURN node1,node2,r";
//		try {
//			runQuery(query);
//		} catch (IOException e) {
//			// TODO Auto-generated catch block
//			e.printStackTrace();
//		}
//		
//	}
//	
///**
// * close the graph database
// */
//	public void shutDown() {
//		System.out.println("*************\n");
//		
//		// START SNIPPET: shutdownServer
//		graphDb.shutdown();
//		System.out.println("database is shut down.");
//		System.out.println("\n*************\n");
//		// END SNIPPET: shutdownServer
//	}
//	
//	
///**
// * Registers a shutdown hook for the Neo4j instance so that 
// * shuts down nicely when the VM exits (even if you "Ctrl-C" the
// * running example before it's completed)
// * @param graphDb
// */
//	// START SNIPPET: shutdownHook
//	private static void registerShutdownHook(final GraphDatabaseService graphDb) { 
//		Runtime.getRuntime().addShutdownHook(new Thread() {
//			@Override
//			public void run() {
//				graphDb.shutdown();
//			}
//		});
//	}
//	// END SNIPPET: shutdownHook
//
//}
