CREATE SCHEMA IF NOT EXISTS content;


CREATE TYPE gender AS ENUM ('Male', 'Female', 'Unknown');


CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    file_path TEXT,
    rating FLOAT,
    type TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);
CREATE INDEX film_work_id_idx ON content.film_work(id);


CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
);
CREATE INDEX genre_id_idx ON content.genre(id);


CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) MATCH FULL ON DELETE CASCADE,
    genre_id uuid NOT NULL REFERENCES content.genre (id) MATCH FULL ON DELETE CASCADE,
    created timestamp with time zone,
    CONSTRAINT "genre_film_work_film_work_id_genre_id_uniq" UNIQUE (film_work_id, genre_id)
);
CREATE INDEX genre_film_work_genre_id_idx ON content.genre_film_work(genre_id);
CREATE INDEX genre_film_work_film_work_id_idx ON content.genre_film_work(film_work_id);


CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    gender gender NOT NULL DEFAULT 'Unknown',
    created timestamp with time zone,
    modified timestamp with time zone
);
CREATE INDEX person_id_idx ON content.person(id);


CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) MATCH FULL ON DELETE CASCADE,
    person_id uuid NOT NULL REFERENCES content.person (id) MATCH FULL ON DELETE CASCADE,
    role TEXT NOT NULL,
    created timestamp with time zone,
    CONSTRAINT "person_film_work_film_work_id_person_id_role_uniq" UNIQUE (film_work_id, person_id, role)
);
CREATE INDEX person_film_work_person_id_idx ON content.person_film_work(person_id);
CREATE INDEX person_film_work_film_work_id_idx ON content.person_film_work(film_work_id);