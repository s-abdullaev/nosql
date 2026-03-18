"""Seed the Neo4j database with the sample graph (persons, places, relationships)."""

from neo4j import GraphDatabase

from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

SEED_CYPHER = """
// Clear existing data
MATCH (n) DETACH DELETE n
;

// ── Continents ───────────────────────────────────────────────────────────────
CREATE (europe:Continent       {name: 'Europe'})
CREATE (northAmerica:Continent {name: 'North America'})

// ── Countries ────────────────────────────────────────────────────────────────
CREATE (france:Country          {name: 'France'})
CREATE (uk:Country              {name: 'United Kingdom'})
CREATE (us:Country              {name: 'United States'})
CREATE (england:Country         {name: 'England'})

// ── Regions / States / Départements ──────────────────────────────────────────
CREATE (bourgogne:Region        {name_fr: 'Bourgogne', name_en: 'Burgundy'})
CREATE (coteDor:Departement     {name: "Côte-d'Or"})
CREATE (idaho:State             {name: 'Idaho', abbreviation: 'ID'})

// ── Cities ───────────────────────────────────────────────────────────────────
CREATE (london:City   {name: 'London'})
CREATE (beaune:City   {name: 'Beaune'})

// ── People ───────────────────────────────────────────────────────────────────
CREATE (lucy:Person   {name: 'Lucy'})
CREATE (alain:Person  {name: 'Alain'})
CREATE (marie:Person  {name: 'Marie'})
CREATE (john:Person   {name: 'John'})

// ── WITHIN edges (geographic hierarchy) ──────────────────────────────────────
CREATE (france)-[:WITHIN]->(europe)
CREATE (uk)-[:WITHIN]->(europe)
CREATE (us)-[:WITHIN]->(northAmerica)
CREATE (england)-[:WITHIN]->(uk)
CREATE (bourgogne)-[:WITHIN]->(france)
CREATE (coteDor)-[:WITHIN]->(bourgogne)
CREATE (idaho)-[:WITHIN]->(us)
CREATE (london)-[:WITHIN]->(england)
CREATE (beaune)-[:WITHIN]->(coteDor)

// ── People relationships ─────────────────────────────────────────────────────
CREATE (lucy)-[:BORN_IN]->(idaho)
CREATE (lucy)-[:LIVES_IN]->(london)
CREATE (alain)-[:BORN_IN]->(beaune)
CREATE (alain)-[:LIVES_IN]->(london)
CREATE (marie)-[:BORN_IN]->(beaune)
CREATE (marie)-[:LIVES_IN]->(beaune)
CREATE (john)-[:BORN_IN]->(london)
CREATE (john)-[:LIVES_IN]->(london)
CREATE (lucy)-[:MARRIED]->(alain)

// ── Friendships ──────────────────────────────────────────────────────────────
CREATE (lucy)-[:FRIENDS {since: 2010}]->(marie)
CREATE (alain)-[:FRIENDS {since: 2005}]->(marie)
CREATE (lucy)-[:FRIENDS {since: 2018}]->(john)
CREATE (john)-[:FRIENDS {since: 2015}]->(alain)
"""


def seed():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        for statement in SEED_CYPHER.split(";"):
            stmt = statement.strip()
            if stmt:
                session.run(stmt)
    driver.close()
    print("Neo4j database seeded successfully.")


if __name__ == "__main__":
    seed()
