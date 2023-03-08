
--CREATE DATABASE gettowork_main
--    WITH
--    OWNER = postgres
--    ENCODING = 'UTF8'
--    LC_COLLATE = 'English_United States.1252'
--    LC_CTYPE = 'English_United States.1252'
--    TABLESPACE = pg_default
--    CONNECTION LIMIT = -1
--    IS_TEMPLATE = False;

DO $$
BEGIN

    CREATE EXTENSION IF NOT EXISTS postgis
        SCHEMA public
        VERSION "3.3.2";


    -- Table: public.users
    DROP TABLE IF EXISTS public.users;
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
      driver_route geometry;
    BEGIN
      driver_route := (select ST_Transform(route, 3857) from driver_routes where driver_routes.id = _driver_id);
      RETURN QUERY
          SELECT passenger_bio.id, passenger_bio.phone, passenger_bio.name,
          ST_Distance(ST_Transform(start_point, 3857),driver_route),
          ST_Distance(ST_Transform(finish_point, 3857), driver_route)
          FROM passenger_bio, passenger_routes
          WHERE ST_Distance(ST_Transform(start_point, 3857),driver_route) < _max_distance
          OR ST_Distance(ST_Transform(finish_point, 3857), driver_route) < _max_distance;
      END; $$
    LANGUAGE 'plpgsql';

   DROP FUNCTION IF EXISTS get_drivers_near_passenger(bigint, bigint);
    CREATE OR REPLACE FUNCTION get_drivers_near_passenger(_id bigint, _max_distance bigint)
    returns table (
      id bigint,
      phone text,
      name text,
      start_point_distance float,
      end_point_distance float) as
    $$
    DECLARE
      _start_point geometry;
      _finish_point geometry;
    BEGIN
      _start_point := (select ST_Transform(start_point, 3857) from passenger_routes where passenger_routes.id = _id);
      _finish_point := (select ST_Transform(finish_point, 3857) from passenger_routes where passenger_routes.id = _id);
      RETURN QUERY
          SELECT driver_bio.id, driver_bio.phone, driver_bio.name,
          ST_Distance(ST_Transform(driver_routes.route, 3857),_start_point),
          ST_Distance(ST_Transform(driver_routes.route, 3857), _finish_point)
          FROM driver_bio, driver_routes
          WHERE ST_Distance(ST_Transform(driver_routes.route, 3857),_start_point) < _max_distance
          OR ST_Distance(ST_Transform(driver_routes.route, 3857), _finish_point) < _max_distance;
      END; $$
    LANGUAGE 'plpgsql';

END; $$