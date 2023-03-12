DO $$
BEGIN

    CREATE EXTENSION IF NOT EXISTS postgis
        SCHEMA public
        VERSION "3.3.2";


    -- Table: public.users
    DROP TABLE IF EXISTS public.users CASCADE;
    CREATE TABLE IF NOT EXISTS public.users
    (
        id bigint NOT NULL,
        role text COLLATE pg_catalog."default",
        is_active boolean,
        CONSTRAINT users_pkey PRIMARY KEY (id)
    )
    TABLESPACE pg_default;
    ALTER TABLE IF EXISTS public.users OWNER to postgres;


    -- Table: public.driver_bio
    DROP TABLE IF EXISTS public.driver_bio;
    CREATE TABLE IF NOT EXISTS public.driver_bio
    (
        id bigint NOT NULL,
        name text COLLATE pg_catalog."default",
        phone text COLLATE pg_catalog."default",
        passengers_count integer,
        FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
    )
    TABLESPACE pg_default;
    ALTER TABLE IF EXISTS public.driver_bio OWNER to postgres;


    -- Table: public.driver_routes
    DROP TABLE IF EXISTS public.driver_routes;
    CREATE TABLE IF NOT EXISTS public.driver_routes
    (
        id bigint NOT NULL,
        start_point geometry,
        start_point_wkt text COLLATE pg_catalog."default",
        finish_point geometry,
        finish_point_wkt text COLLATE pg_catalog."default",
        route geometry,
        route_wkt text COLLATE pg_catalog."default",
        FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
    )
    TABLESPACE pg_default;
    ALTER TABLE IF EXISTS public.driver_routes OWNER to postgres;


    -- Table: public.passenger_bio
    DROP TABLE IF EXISTS public.passenger_bio;
    CREATE TABLE IF NOT EXISTS public.passenger_bio
    (
        id bigint NOT NULL,
        name text COLLATE pg_catalog."default",
        phone text COLLATE pg_catalog."default",
        FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
    )
    TABLESPACE pg_default;
    ALTER TABLE IF EXISTS public.passenger_bio OWNER to postgres;


    -- Table: public.passenger_routes
    DROP TABLE IF EXISTS public.passenger_routes;
    CREATE TABLE IF NOT EXISTS public.passenger_routes
    (
        id bigint NOT NULL,
        start_point geometry,
        start_point_wkt text COLLATE pg_catalog."default",
        finish_point geometry,
        finish_point_wkt text COLLATE pg_catalog."default",
        route geometry,
        route_wkt text COLLATE pg_catalog."default",
        FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
    )
    TABLESPACE pg_default;
    ALTER TABLE IF EXISTS public.passenger_routes OWNER to postgres;


  

END$$;



DROP FUNCTION IF EXISTS get_passengers_near_driver_route(bigint, bigint);
CREATE OR REPLACE FUNCTION get_passengers_near_driver_route(_driver_id bigint, _max_distance bigint)
returns table (
  id bigint,
  phone text,
  name text,
  start_point_distance float,
  end_point_distance float) as
$$
DECLARE
  _driver_route geometry;
BEGIN
  _driver_route := (select route from driver_routes where driver_routes.id = _driver_id);
  RETURN QUERY
	  SELECT passenger_bio.id, passenger_bio.phone, passenger_bio.name,
	  ST_Distance(start_point, _driver_route),
	  ST_Distance(finish_point, _driver_route)
	  FROM passenger_bio JOIN passenger_routes ON passenger_bio.id=passenger_routes.id
	  WHERE ST_Distance(start_point, _driver_route) <= _max_distance
	  AND ST_Distance(finish_point, _driver_route) <= _max_distance;
  END; $$
LANGUAGE 'plpgsql';

DROP FUNCTION IF EXISTS get_drivers_near_passenger(bigint, bigint);
CREATE OR REPLACE FUNCTION public.get_drivers_near_passenger(
	_id bigint,
	_max_distance bigint)
    RETURNS TABLE(id bigint, phone text, name text, start_point_distance double precision, end_point_distance double precision)
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
DECLARE
  _start_point geometry;
  _finish_point geometry;
BEGIN
  _start_point := (select start_point from passenger_routes where passenger_routes.id = _id);
  _finish_point := (select finish_point from passenger_routes where passenger_routes.id = _id);
  RETURN QUERY
	  SELECT driver_bio.id, driver_bio.phone, driver_bio.name,
	  ST_Distance(driver_routes.route, _start_point),
	  ST_Distance(driver_routes.route, _finish_point)
	  FROM driver_bio JOIN driver_routes ON driver_bio.id=driver_routes.id
	  WHERE ST_Distance(driver_routes.route,_start_point) <= _max_distance
	  AND ST_Distance(driver_routes.route, _finish_point) <= _max_distance;
  END;
$BODY$;
	
