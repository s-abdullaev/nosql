from fastapi import APIRouter, Depends, HTTPException, Query
from neo4j import Session as Neo4jSession

from app.database import get_neo4j

router = APIRouter(prefix="/neo4j", tags=["neo4j"])


# ── Node Queries ──────────────────────────────────────────────────────────────


@router.get("/persons")
def list_persons(neo4j: Neo4jSession = Depends(get_neo4j)):
    """List all persons with their born_in and lives_in locations."""
    result = neo4j.run("""
        MATCH (p:Person)
        OPTIONAL MATCH (p)-[:BORN_IN]->(birth)
        OPTIONAL MATCH (p)-[:LIVES_IN]->(home)
        RETURN p.name AS name,
               labels(birth)[0] AS birth_type, birth.name AS born_in,
               labels(home)[0]  AS home_type,  home.name  AS lives_in
    """)
    return {"persons": [dict(r) for r in result]}


@router.get("/locations")
def list_locations(neo4j: Neo4jSession = Depends(get_neo4j)):
    """List every location node (City, State, Region, Country, Continent, Departement)."""
    result = neo4j.run("""
        MATCH (n)
        WHERE n:City OR n:State OR n:Region OR n:Country OR n:Continent OR n:Departement
        RETURN labels(n)[0] AS type,
               coalesce(n.name, n.name_fr) AS name,
               properties(n) AS props
        ORDER BY type, name
    """)
    return {"locations": [dict(r) for r in result]}


# ── Key Graph Queries ─────────────────────────────────────────────────────────


@router.get("/persons/born-and-live-different-country")
def born_and_live_different_country(neo4j: Neo4jSession = Depends(get_neo4j)):
    """Find people who were born in one country but live in another."""
    result = neo4j.run("""
        MATCH (p:Person)-[:BORN_IN]->(birthPlace)-[:WITHIN*0..]->(birthCountry:Country),
              (p)-[:LIVES_IN]->(homePlace)-[:WITHIN*0..]->(homeCountry:Country)
        WHERE birthCountry <> homeCountry
        RETURN p.name          AS person,
               birthPlace.name AS born_in,
               birthCountry.name AS birth_country,
               homePlace.name  AS lives_in,
               homeCountry.name AS living_country
    """)
    return {"persons": [dict(r) for r in result]}


@router.get("/persons/born-and-live-different-continent")
def born_and_live_different_continent(neo4j: Neo4jSession = Depends(get_neo4j)):
    """Find people who were born on one continent but live on another."""
    result = neo4j.run("""
        MATCH (p:Person)-[:BORN_IN]->(bp)-[:WITHIN*0..]->(bc:Continent),
              (p)-[:LIVES_IN]->(hp)-[:WITHIN*0..]->(hc:Continent)
        WHERE bc <> hc
        RETURN p.name    AS person,
               bp.name   AS born_in,
               bc.name   AS birth_continent,
               hp.name   AS lives_in,
               hc.name   AS living_continent
    """)
    return {"persons": [dict(r) for r in result]}


@router.get("/persons/live-in-same-city")
def live_in_same_city(neo4j: Neo4jSession = Depends(get_neo4j)):
    """Find pairs of people who live in the same city."""
    result = neo4j.run("""
        MATCH (p1:Person)-[:LIVES_IN]->(c:City)<-[:LIVES_IN]-(p2:Person)
        WHERE id(p1) < id(p2)
        RETURN p1.name AS person1, p2.name AS person2, c.name AS city
    """)
    return {"pairs": [dict(r) for r in result]}


@router.get("/persons/married")
def married_couples(neo4j: Neo4jSession = Depends(get_neo4j)):
    """List all married couples."""
    result = neo4j.run("""
        MATCH (p1:Person)-[:MARRIED]-(p2:Person)
        WHERE id(p1) < id(p2)
        RETURN p1.name AS person1, p2.name AS person2
    """)
    return {"couples": [dict(r) for r in result]}


@router.get("/locations/{name}/hierarchy")
def location_hierarchy(name: str, neo4j: Neo4jSession = Depends(get_neo4j)):
    """Get the full geographic hierarchy for a location (e.g. Beaune -> ... -> Europe)."""
    result = neo4j.run("""
        MATCH (n)-[:WITHIN*0..]->(parent)
        WHERE n.name = $name OR n.name_fr = $name
        RETURN [node IN nodes((n)-[:WITHIN*0..]->(parent)) |
                {type: labels(node)[0], name: coalesce(node.name, node.name_fr)}
               ] AS chain
        ORDER BY length((n)-[:WITHIN*0..]->(parent)) DESC
        LIMIT 1
    """, name=name)
    record = result.single()
    if not record:
        raise HTTPException(404, f"Location '{name}' not found")
    return {"location": name, "hierarchy": record["chain"]}


@router.get("/locations/{name}/within")
def locations_within(name: str, neo4j: Neo4jSession = Depends(get_neo4j)):
    """Find all locations contained within a given location (recursive)."""
    result = neo4j.run("""
        MATCH (child)-[:WITHIN*1..]->(parent)
        WHERE parent.name = $name OR parent.name_fr = $name
        RETURN labels(child)[0] AS type,
               coalesce(child.name, child.name_fr) AS name,
               properties(child) AS props
        ORDER BY type, name
    """, name=name)
    return {"parent": name, "contains": [dict(r) for r in result]}


@router.get("/persons/{name}/connections")
def person_connections(name: str, neo4j: Neo4jSession = Depends(get_neo4j)):
    """Get all direct relationships of a person."""
    result = neo4j.run("""
        MATCH (p:Person {name: $name})-[r]->(target)
        RETURN type(r) AS relationship,
               labels(target)[0] AS target_type,
               coalesce(target.name, target.name_fr) AS target_name
    """, name=name)
    rows = [dict(r) for r in result]
    if not rows:
        raise HTTPException(404, f"Person '{name}' not found or has no connections")
    return {"person": name, "connections": rows}


@router.get("/shortest-path")
def shortest_path(
    from_name: str = Query(..., description="Name of the start node"),
    to_name: str = Query(..., description="Name of the end node"),
    neo4j: Neo4jSession = Depends(get_neo4j),
):
    """Find the shortest path between any two named nodes."""
    result = neo4j.run("""
        MATCH (a), (b)
        WHERE (a.name = $from_name OR a.name_fr = $from_name)
          AND (b.name = $to_name   OR b.name_fr = $to_name)
        MATCH path = shortestPath((a)-[*]-(b))
        RETURN [n IN nodes(path) |
                {type: labels(n)[0], name: coalesce(n.name, n.name_fr)}
               ] AS nodes,
               [r IN relationships(path) | type(r)] AS relationships,
               length(path) AS hops
    """, from_name=from_name, to_name=to_name)
    record = result.single()
    if not record:
        raise HTTPException(404, "No path found between the two nodes")
    return {
        "from": from_name,
        "to": to_name,
        "hops": record["hops"],
        "nodes": record["nodes"],
        "relationships": record["relationships"],
    }


@router.get("/persons/born-in-country/{country}")
def persons_born_in_country(country: str, neo4j: Neo4jSession = Depends(get_neo4j)):
    """Find all people born in (or within) a given country."""
    result = neo4j.run("""
        MATCH (p:Person)-[:BORN_IN]->(place)-[:WITHIN*0..]->(c:Country {name: $country})
        RETURN p.name AS person, place.name AS born_in
    """, country=country)
    rows = [dict(r) for r in result]
    return {"country": country, "persons": rows}


@router.get("/persons/living-in-country/{country}")
def persons_living_in_country(country: str, neo4j: Neo4jSession = Depends(get_neo4j)):
    """Find all people living in (or within) a given country."""
    result = neo4j.run("""
        MATCH (p:Person)-[:LIVES_IN]->(place)-[:WITHIN*0..]->(c:Country {name: $country})
        RETURN p.name AS person, place.name AS lives_in
    """, country=country)
    rows = [dict(r) for r in result]
    return {"country": country, "persons": rows}


@router.get("/stats")
def graph_stats(neo4j: Neo4jSession = Depends(get_neo4j)):
    """Get summary statistics of the graph."""
    nodes = neo4j.run("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS count ORDER BY label")
    rels = neo4j.run("MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count ORDER BY type")
    return {
        "nodes_by_label": {r["label"]: r["count"] for r in nodes},
        "relationships_by_type": {r["type"]: r["count"] for r in rels},
    }
