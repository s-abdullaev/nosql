
-- ============================================================
-- PostGIS Spatial Query Examples  (geodemo database)
-- Tables: restaurant(id, name, cuisine, address, location POINT)
--         region(id, name, description, boundary POLYGON)
-- ============================================================

-- 1. View restaurant locations as human-readable text
SELECT id, name, ST_AsText(location) AS wkt
FROM restaurant;

-- 2. Get longitude / latitude from a stored point
SELECT id, name,
       ST_X(location) AS longitude,
       ST_Y(location) AS latitude
FROM restaurant;

-- 3. Distance (metres) from every restaurant to the Eiffel Tower
SELECT name,
       ST_Distance(
           location::geography,
           ST_SetSRID(ST_MakePoint(2.2945, 48.8584), 4326)::geography
       ) AS distance_m
FROM restaurant
ORDER BY distance_m;

-- 4. Find restaurants within 1 km of Notre-Dame (2.3499, 48.8530)
SELECT name, address,
       ST_Distance(
           location::geography,
           ST_SetSRID(ST_MakePoint(2.3499, 48.8530), 4326)::geography
       ) AS distance_m
FROM restaurant
WHERE ST_DWithin(
    location::geography,
    ST_SetSRID(ST_MakePoint(2.3499, 48.8530), 4326)::geography,
    1000
)
ORDER BY distance_m;

-- 5. Which region contains each restaurant?
SELECT r.name  AS restaurant,
       rg.name AS region
FROM restaurant r
JOIN region rg ON ST_Contains(rg.boundary, r.location);

-- 6. Restaurants that fall inside the "Saint-Germain-des-Prés" region
SELECT r.name, r.address
FROM restaurant r
JOIN region rg ON ST_Contains(rg.boundary, r.location)
WHERE rg.name = 'Saint-Germain-des-Prés';

-- 7. Area of each region in square metres (cast to geography for metric units)
SELECT name,
       ST_Area(boundary::geography) AS area_m2
FROM region
ORDER BY area_m2 DESC;

-- 8. Regions whose boundaries overlap "Rive Gauche Centre"
SELECT a.name AS region_a,
       b.name AS region_b
FROM region a
JOIN region b ON ST_Intersects(a.boundary, b.boundary)
                 AND a.id < b.id;

-- 9. Compute the intersection polygon between two overlapping regions
SELECT a.name AS region_a,
       b.name AS region_b,
       ST_AsText(ST_Intersection(a.boundary, b.boundary)) AS overlap_wkt,
       ST_Area(ST_Intersection(a.boundary, b.boundary)::geography) AS overlap_m2
FROM region a
JOIN region b ON ST_Intersects(a.boundary, b.boundary)
                 AND a.id < b.id;

-- 10. Bounding box of a region
SELECT name,
       ST_AsText(ST_Envelope(boundary)) AS bbox
FROM region;

-- 11. Centroid of each region
SELECT name,
       ST_X(ST_Centroid(boundary)) AS centroid_lon,
       ST_Y(ST_Centroid(boundary)) AS centroid_lat
FROM region;

-- 12. Perimeter of each region in metres
SELECT name,
       ST_Perimeter(boundary::geography) AS perimeter_m
FROM region
ORDER BY perimeter_m DESC;

-- 13. Buffer: create a 500 m zone around a restaurant and find neighbours
WITH buf AS (
    SELECT name,
           ST_Buffer(location::geography, 500)::geometry AS zone
    FROM restaurant
    WHERE name = 'Café de Flore'
)
SELECT buf.name AS origin,
       r.name   AS neighbour,
       ST_Distance(r.location::geography,
                   ST_Centroid(buf.zone)::geography) AS distance_m
FROM buf
JOIN restaurant r ON ST_Intersects(r.location, buf.zone)
                     AND r.name <> buf.name
ORDER BY distance_m;

-- 14. Union of all region boundaries into a single geometry
SELECT ST_AsText(ST_Union(boundary)) AS merged_wkt
FROM region;

-- 15. GeoJSON export (useful for web map clients)
SELECT name,
       ST_AsGeoJSON(location)::json AS geojson
FROM restaurant;

-- 16. K-nearest neighbours: 3 closest restaurants to Panthéon (2.3461, 48.8462)
SELECT name, address,
       ST_Distance(
           location::geography,
           ST_SetSRID(ST_MakePoint(2.3461, 48.8462), 4326)::geography
       ) AS distance_m
FROM restaurant
ORDER BY location <-> ST_SetSRID(ST_MakePoint(2.3461, 48.8462), 4326)
LIMIT 3;

-- 17. Create a spatial index for faster queries (run once)
-- CREATE INDEX idx_restaurant_location ON restaurant USING GIST (location);
-- CREATE INDEX idx_region_boundary     ON region     USING GIST (boundary);
