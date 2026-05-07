CREATE SCHEMA rating;

SET search_path TO rating;

CREATE TABLE IF NOT EXISTS movies (
    id           BIGINT PRIMARY KEY,
    title        VARCHAR,
    genres       VARCHAR,
    release_year SMALLINT,
    metadata     JSONB
);

CREATE TABLE IF NOT EXISTS users (
    id         BIGINT PRIMARY KEY,
    gender     VARCHAR(4),
    age        SMALLINT,
    occupation INTEGER,
    zipcode    VARCHAR(10)
);

CREATE TABLE IF NOT EXISTS ratings (
    user_id    BIGINT,
    movie_id   BIGINT,
    rating     FLOAT,
    timestamp  TIMESTAMP(3),
    PRIMARY KEY (user_id, movie_id)
);