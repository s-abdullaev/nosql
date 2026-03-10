import json

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2 import WKTElement
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Region, Restaurant
from app.database import get_postgis_db
from app.schema import (
    RegionCreate,
    RegionUpdate,
    RestaurantCreate,
    RestaurantUpdate,
)

router = APIRouter(prefix="/postgis", tags=["postgis"])


# ── Helpers ──────────────────────────────────────────────────────────────────


def _serialize_restaurant(r: Restaurant) -> dict:
    point = to_shape(r.location)
    return {
        "id": r.id,
        "name": r.name,
        "cuisine": r.cuisine,
        "address": r.address,
        "latitude": point.y,
        "longitude": point.x,
    }


def _serialize_region(r: Region) -> dict:
    poly = to_shape(r.boundary)
    return {
        "id": r.id,
        "name": r.name,
        "description": r.description,
        "boundary": mapping(poly),
    }


def _make_point(lon: float, lat: float) -> WKTElement:
    return WKTElement(f"POINT({lon} {lat})", srid=4326)


def _make_polygon(coordinates: list[list[float]]) -> WKTElement:
    """Build a WKT polygon from a ring of [lon, lat] pairs (auto-closes)."""
    if coordinates[0] != coordinates[-1]:
        coordinates = [*coordinates, coordinates[0]]
    ring = ", ".join(f"{lon} {lat}" for lon, lat in coordinates)
    return WKTElement(f"POLYGON(({ring}))", srid=4326)


# ── Spatial Queries ──────────────────────────────────────────────────────────


@router.get("/restaurants/distance")
def restaurants_distance(
    latitude: float = Query(...),
    longitude: float = Query(...),
    db: Session = Depends(get_postgis_db),
):
    """Distance (meters) from a point to every restaurant, sorted nearest-first."""
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)

    distance_expr = func.ST_Distance(
        func.Geography(Restaurant.location),
        func.Geography(point),
    ).label("distance")

    rows = db.query(Restaurant, distance_expr).order_by(distance_expr).all()

    restaurants = []
    for r, dist in rows:
        data = _serialize_restaurant(r)
        data["distance_meters"] = round(dist, 2)
        restaurants.append(data)

    return {
        "reference_point": {"latitude": latitude, "longitude": longitude},
        "count": len(restaurants),
        "restaurants": restaurants,
    }


@router.get("/restaurants/nearby")
def restaurants_nearby(
    latitude: float = Query(...),
    longitude: float = Query(...),
    max_distance: float = Query(..., description="Maximum distance in meters"),
    db: Session = Depends(get_postgis_db),
):
    """Find restaurants within a given distance of a point."""
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)

    distance_expr = func.ST_Distance(
        func.Geography(Restaurant.location),
        func.Geography(point),
    ).label("distance")

    rows = (
        db.query(Restaurant, distance_expr)
        .filter(
            func.ST_DWithin(
                func.Geography(Restaurant.location),
                func.Geography(point),
                max_distance,
            )
        )
        .order_by(distance_expr)
        .all()
    )

    restaurants = []
    for r, dist in rows:
        data = _serialize_restaurant(r)
        data["distance_meters"] = round(dist, 2)
        restaurants.append(data)

    return {
        "reference_point": {"latitude": latitude, "longitude": longitude},
        "max_distance_meters": max_distance,
        "count": len(restaurants),
        "restaurants": restaurants,
    }


@router.get("/regions/intersection")
def region_intersection(
    region1_id: int = Query(...),
    region2_id: int = Query(...),
    db: Session = Depends(get_postgis_db),
):
    """Compute the intersection of two regions."""
    r1 = db.get(Region, region1_id)
    r2 = db.get(Region, region2_id)
    if not r1:
        raise HTTPException(404, f"Region {region1_id} not found")
    if not r2:
        raise HTTPException(404, f"Region {region2_id} not found")

    g1 = select(Region.boundary).where(Region.id == region1_id).scalar_subquery()
    g2 = select(Region.boundary).where(Region.id == region2_id).scalar_subquery()

    intersects = db.scalar(select(func.ST_Intersects(g1, g2)))

    result: dict = {
        "region1": _serialize_region(r1),
        "region2": _serialize_region(r2),
        "intersects": intersects,
        "intersection": None,
        "intersection_area_sq_meters": None,
    }

    if intersects:
        geojson_str = db.scalar(select(func.ST_AsGeoJSON(func.ST_Intersection(g1, g2))))
        result["intersection"] = json.loads(geojson_str)
        area = db.scalar(
            select(func.ST_Area(func.Geography(func.ST_Intersection(g1, g2))))
        )
        result["intersection_area_sq_meters"] = round(area, 2)

    return result


@router.get("/regions/{region_id}/restaurants")
def restaurants_in_region(region_id: int, db: Session = Depends(get_postgis_db)):
    """Find all restaurants contained within a region (ST_Contains)."""
    region = db.get(Region, region_id)
    if not region:
        raise HTTPException(404, f"Region {region_id} not found")

    boundary = select(Region.boundary).where(Region.id == region_id).scalar_subquery()

    restaurants = (
        db.query(Restaurant)
        .filter(func.ST_Contains(boundary, Restaurant.location))
        .all()
    )

    return {
        "region": _serialize_region(region),
        "count": len(restaurants),
        "restaurants": [_serialize_restaurant(r) for r in restaurants],
    }


@router.get("/regions/{region_id}/area")
def region_area(region_id: int, db: Session = Depends(get_postgis_db)):
    """Calculate the area of a region using geography (result in sq meters)."""
    region = db.get(Region, region_id)
    if not region:
        raise HTTPException(404, f"Region {region_id} not found")

    area_m2 = db.scalar(
        select(func.ST_Area(func.Geography(Region.boundary))).where(
            Region.id == region_id
        )
    )

    return {
        "region": _serialize_region(region),
        "area_sq_meters": round(area_m2, 2),
        "area_sq_km": round(area_m2 / 1_000_000, 4),
    }


# ── Restaurant CRUD ──────────────────────────────────────────────────────────


@router.get("/restaurants")
def list_restaurants(db: Session = Depends(get_postgis_db)):
    restaurants = db.query(Restaurant).all()
    return {"restaurants": [_serialize_restaurant(r) for r in restaurants]}


@router.post("/restaurants", status_code=201)
def create_restaurant(body: RestaurantCreate, db: Session = Depends(get_postgis_db)):
    r = Restaurant(
        name=body.name,
        cuisine=body.cuisine,
        address=body.address,
        location=_make_point(body.longitude, body.latitude),
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return _serialize_restaurant(r)


@router.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_postgis_db)):
    r = db.get(Restaurant, restaurant_id)
    if not r:
        raise HTTPException(404, f"Restaurant {restaurant_id} not found")
    return _serialize_restaurant(r)


@router.put("/restaurants/{restaurant_id}")
def update_restaurant(
    restaurant_id: int,
    body: RestaurantUpdate,
    db: Session = Depends(get_postgis_db),
):
    r = db.get(Restaurant, restaurant_id)
    if not r:
        raise HTTPException(404, f"Restaurant {restaurant_id} not found")

    if body.name is not None:
        r.name = body.name
    if body.cuisine is not None:
        r.cuisine = body.cuisine
    if body.address is not None:
        r.address = body.address
    if body.latitude is not None or body.longitude is not None:
        current = to_shape(r.location)
        lon = body.longitude if body.longitude is not None else current.x
        lat = body.latitude if body.latitude is not None else current.y
        r.location = _make_point(lon, lat)

    db.commit()
    db.refresh(r)
    return _serialize_restaurant(r)


@router.delete("/restaurants/{restaurant_id}")
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_postgis_db)):
    r = db.get(Restaurant, restaurant_id)
    if not r:
        raise HTTPException(404, f"Restaurant {restaurant_id} not found")
    db.delete(r)
    db.commit()
    return {"message": f"Restaurant {restaurant_id} deleted"}


# ── Region CRUD ──────────────────────────────────────────────────────────────


@router.get("/regions")
def list_regions(db: Session = Depends(get_postgis_db)):
    regions = db.query(Region).all()
    return {"regions": [_serialize_region(r) for r in regions]}


@router.post("/regions", status_code=201)
def create_region(body: RegionCreate, db: Session = Depends(get_postgis_db)):
    r = Region(
        name=body.name,
        description=body.description,
        boundary=_make_polygon(body.coordinates),
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return _serialize_region(r)


@router.get("/regions/{region_id}")
def get_region(region_id: int, db: Session = Depends(get_postgis_db)):
    r = db.get(Region, region_id)
    if not r:
        raise HTTPException(404, f"Region {region_id} not found")
    return _serialize_region(r)


@router.put("/regions/{region_id}")
def update_region(
    region_id: int,
    body: RegionUpdate,
    db: Session = Depends(get_postgis_db),
):
    r = db.get(Region, region_id)
    if not r:
        raise HTTPException(404, f"Region {region_id} not found")

    if body.name is not None:
        r.name = body.name
    if body.description is not None:
        r.description = body.description
    if body.coordinates is not None:
        r.boundary = _make_polygon(body.coordinates)

    db.commit()
    db.refresh(r)
    return _serialize_region(r)


@router.delete("/regions/{region_id}")
def delete_region(region_id: int, db: Session = Depends(get_postgis_db)):
    r = db.get(Region, region_id)
    if not r:
        raise HTTPException(404, f"Region {region_id} not found")
    db.delete(r)
    db.commit()
    return {"message": f"Region {region_id} deleted"}
