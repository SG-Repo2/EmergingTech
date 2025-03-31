from neo4j import GraphDatabase

def run_query(query):
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "8aPaBe8X3mGEsYcXzvUhHwjrC9rV64LmrSVXIE_X-Wk"
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        with driver.session() as session:
            result = session.run(query)
            # Get the column names
            columns = result.keys()
            print("\nColumns:", ", ".join(columns))
            print("-" * 80)
            
            # Print each record
            for record in result:
                values = [str(value) for value in record.values()]
                print(" | ".join(values))
    finally:
        driver.close()

# Query 1: Sam Altman's Career Path
print("\n=== Sam Altman's Career Path ===")
run_query("""
MATCH (sa:Person {name: 'Sam Altman'})-[r]->(org)
RETURN org.name as Organization, type(r) as Role, org.Notes as Description
ORDER BY type(r)
""")

# Query 2: OpenAI's Product Timeline
print("\n=== OpenAI's Product Timeline ===")
run_query("""
MATCH (openai:Company {name: 'OpenAI'})-[:Developed]->(product)
WHERE product.node_type = 'Product/Service'
RETURN product.name as Product, product.Notes as Description
""")

# Query 3: OpenAI's Competitive Landscape
print("\n=== OpenAI's Competitive Landscape ===")
run_query("""
MATCH (openai:Company {name: 'OpenAI'})-[:Competitor]->(competitor)
RETURN competitor.name as Competitor, competitor.Notes as Description
""")

# Query 4: OpenAI's Technology Stack
print("\n=== OpenAI's Technology Stack ===")
run_query("""
MATCH (openai:Company {name: 'OpenAI'})-[:Uses_Technology]->(tech)
RETURN tech.name as Technology, tech.Notes as Description
""")

# Query 5: OpenAI's Key People
print("\n=== OpenAI's Key People ===")
run_query("""
MATCH (person:Person)-[r]->(openai:Company {name: 'OpenAI'})
RETURN person.name as Person, type(r) as Role, person.Notes as Description
""")

# Query 6: Y Combinator Network
print("\n=== Y Combinator Network ===")
run_query("""
MATCH (yc:Company {name: 'Y Combinator (YC)'})<-[r]-(entity)
RETURN entity.name as Entity, type(r) as Relationship, entity.Notes as Description
""")

# Query 7: Microsoft's OpenAI Integration
print("\n=== Microsoft's OpenAI Integration ===")
run_query("""
MATCH (microsoft:Company {name: 'Microsoft'})-[r]-(entity)
WHERE entity.name IN ['OpenAI', 'New Bing', 'Kevin Scott']
RETURN entity.name as Entity, type(r) as Relationship, entity.Notes as Description
""")

# Query 8: OpenAI's Research Goals
print("\n=== OpenAI's Research Goals ===")
run_query("""
MATCH (openai:Company {name: 'OpenAI'})-[:Research_Goal]->(goal)
RETURN goal.name as Goal, goal.Notes as Description
""")

# Query 9: Companies Using OpenAI Technology
print("\n=== Companies Using OpenAI Technology ===")
run_query("""
MATCH (company)-[:Uses_Technology]->(openai:Company {name: 'OpenAI'})
RETURN company.name as Company, company.Notes as Description
""")

# Query 10: OpenAI's Origin Story
print("\n=== OpenAI's Origin Story ===")
run_query("""
MATCH (entity)-[r]->(openai:Company {name: 'OpenAI'})
WHERE type(r) IN ['Co_Founder', 'Hosted_Pivotal_Meeting']
RETURN entity.name as Entity, type(r) as Role, entity.Notes as Description
""")

# Query 1: Nvidia's GPU Product Line
print("\nQuery 1: Nvidia's GPU Product Line:")
run_query("""
MATCH (n:Product_Service)
WHERE n.Entity_Type CONTAINS 'Nvidia GPU'
RETURN n.name as GPU, n.Entity_Type as Type
ORDER BY n.name
""")

# Query 2: Nvidia's Foundry and Memory Suppliers
print("\nQuery 2: Nvidia's Foundry and Memory Suppliers:")
run_query("""
MATCH (n:Nvidia)-[r]->(s:Company)
WHERE TYPE(r) IN ['Foundry_Partner', 'Has_Memory_Supplier']
RETURN TYPE(r) as RelationshipType, s.name as Supplier
ORDER BY RelationshipType, Supplier
""")

# Query 3: Companies Adopting GB300
print("\nQuery 3: Companies Adopting GB300:")
run_query("""
MATCH (c:Company)-[:Adopts]->(g:Product_Service)
WHERE g.name = 'GB300'
RETURN c.name as Company, c.Entity_Type as CompanyType
ORDER BY Company
""")

# Query 4: Nvidia's Technology Stack
print("\nQuery 4: Nvidia's Technology Stack:")
run_query("""
MATCH (n:Nvidia)-[:Develops]->(t:Technology)
RETURN t.name as Technology, t.Entity_Type as Type
ORDER BY Type, Technology
""")

# Query 5: Nvidia's Supply Chain Status
print("\nQuery 5: Nvidia's Supply Chain Status:")
run_query("""
MATCH (n:Nvidia)-[r:Supply_Relationship]->(s:Company)
RETURN s.name as Supplier, r.status as Status
ORDER BY Status, Supplier
""")

# Query 6: Blackwell Architecture Products
print("\nQuery 6: Products Based on Blackwell Architecture:")
run_query("""
MATCH (p:Product_Service)-[:Is_Based_On]->(b:Technology)
WHERE b.name = 'Blackwell'
RETURN p.name as Product, p.Entity_Type as Type
ORDER BY Product
""")

# Query 7: Nvidia's Co-Founders
print("\nQuery 7: Nvidia's Co-Founders:")
run_query("""
MATCH (n:Nvidia)-[:Has_CoFounder]->(p:Person)
RETURN p.name as CoFounder, p.Entity_Type as Role
ORDER BY CoFounder
""")

# Query 8: Companies Developing AI Chips
print("\nQuery 8: Companies Developing AI Chips:")
run_query("""
MATCH (c:Company)-[:Develops]->(p:Product_Service)
WHERE p.Entity_Type CONTAINS 'AI Chip'
RETURN c.name as Company, p.name as Chip, p.Entity_Type as Type
ORDER BY Company
""")

# Query 9: Nvidia's GPU Cluster Topologies
print("\nQuery 9: Nvidia's GPU Cluster Topologies:")
run_query("""
MATCH (t:Product_Service)
WHERE t.Entity_Type = 'Nvidia GPU Cluster Topology'
RETURN t.name as Topology
ORDER BY t.name
""")

# Query 10: Companies Using Nvidia's Technologies
print("\nQuery 10: Companies Using Nvidia's Technologies:")
run_query("""
MATCH (c:Company)-[r:Adopts|Used_Prior]->(t:Product_Service)
WHERE t.Entity_Type CONTAINS 'Nvidia'
RETURN c.name as Company, TYPE(r) as Relationship, t.name as Technology
ORDER BY Company, Relationship
""")

# Query 1: Node types and counts
print("\nQuery 1: Types of nodes and their counts:")
run_query("""
MATCH (n)
RETURN DISTINCT labels(n) as NodeTypes, count(*) as Count
ORDER BY Count DESC
""")

# Query 2: All relationships types and counts
print("\nQuery 2: Types of relationships and their counts:")
run_query("""
MATCH ()-[r]->()
RETURN TYPE(r) as RelationType, count(*) as Count
ORDER BY Count DESC
""")

# Query 3: Companies by Entity Type
print("\nQuery 3: Companies grouped by Entity Type:")
run_query("""
MATCH (c:Company)
RETURN c.Entity_Type as EntityType, count(*) as Count, 
       collect(c.name) as Companies
ORDER BY Count DESC
""")

# Query 4: Companies by Location
print("\nQuery 4: Companies grouped by Headquarters Location:")
run_query("""
MATCH (c:Company)
WHERE c.Headquarters_Location IS NOT NULL
RETURN c.Headquarters_Location as Location, count(*) as Count,
       collect(c.name) as Companies
ORDER BY Count DESC
""")

# Query 5: Technology Dependencies
print("\nQuery 5: Technology Dependencies and Requirements:")
run_query("""
MATCH (n)-[:Requires]->(t:Technology)
RETURN n.name as Source, t.name as RequiredTechnology,
       n.Notes as SourceNotes, t.Notes as TechnologyNotes
ORDER BY Source
""")

# Query 6: Company Acquisitions
print("\nQuery 6: Company Acquisitions:")
run_query("""
MATCH (c1:Company)-[:Acquired]->(c2:Company)
RETURN c1.name as Acquirer, c2.name as Acquired,
       c2.Entity_Type as AcquiredType, c2.Notes as AcquisitionDetails
ORDER BY Acquirer
""")

# Query 7: AI Infrastructure Companies
print("\nQuery 7: Companies involved in AI Infrastructure:")
run_query("""
MATCH (c:Company)
WHERE c.Primary_Business_Model CONTAINS 'AI' OR c.Notes CONTAINS 'AI'
RETURN c.name as Company, c.Primary_Business_Model as BusinessModel,
       c.Notes as Notes
ORDER BY Company
""")

# Query 8: Power and Cooling Solutions
print("\nQuery 8: Companies providing Power and Cooling Solutions:")
run_query("""
MATCH (c:Company)
WHERE c.Primary_Business_Model CONTAINS 'Power' OR 
      c.Primary_Business_Model CONTAINS 'Cooling'
RETURN c.name as Company, c.Primary_Business_Model as BusinessModel,
       c.Notes as Notes
ORDER BY Company
""")

# Query 9: Competitive Landscape
print("\nQuery 9: Competitive Relationships between Companies:")
run_query("""
MATCH (c1:Company)-[:Competitors]->(c2:Company)
RETURN c1.name as Company1, c2.name as Company2,
       c1.Primary_Business_Model as Company1Business,
       c2.Primary_Business_Model as Company2Business
ORDER BY Company1
""")

# Query 10: Technology Development Chain
print("\nQuery 10: Technology Development Chain:")
run_query("""
MATCH (c:Company)-[:Develops]->(t:Technology)
RETURN c.name as Company, t.name as Technology,
       t.Notes as TechnologyNotes
ORDER BY Company
""")

# Query 11: Datacenter Infrastructure
print("\nQuery 11: Datacenter Infrastructure Components:")
run_query("""
MATCH (t:Technology)
WHERE t.node_type = 'Technology'
RETURN t.name as Technology, t.Notes as Description
ORDER BY Technology
""")

# Query 12: Company Partnerships
print("\nQuery 12: Company Partnerships and Collaborations:")
run_query("""
MATCH (c1:Company)-[r]->(c2:Company)
WHERE TYPE(r) IN ['Provides', 'Supplies', 'Develops']
RETURN c1.name as Company1, TYPE(r) as Relationship,
       c2.name as Company2, r.details as Details
ORDER BY Company1
""") 