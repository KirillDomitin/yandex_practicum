set search_path to content;

with

/* 1. Сначала собираем все film_work_id, в которых были изменения */

film_work_ids as (
	select
		id
	from
		film_work
	where
		modified > '{movies}'::timestamptz
	),
genre_ids as (
	select
        gfw.film_work_id as id
	from
        genre_film_work as gfw
    join
        genre as g
        on g.id = gfw.genre_id
	where
		gfw.created > '{movies}'::timestamptz
		or g.modified > '{movies}'::timestamptz
	),
person_ids as (
	select
        pfw.film_work_id as id
	from
        person_film_work as pfw
    join
        person as p
        on p.id = pfw.person_id
	where
		pfw.created > '{movies}'::timestamptz
		or p.modified > '{movies}'::timestamptz
	),
ids_filter as (
	select id from film_work_ids
	union distinct
	select id from genre_ids
	union distinct
	select id from person_ids
	),

/* 2. Теперь собираем данные только по id из ids_filter */

genres as (
    select
        gfw.film_work_id as id,
        array_agg(json_build_object('id', g.id, 'name', g.name)) as genres,
        max(greatest(gfw.created, g.modified)) as genres_modified
    from
    	ids_filter as f
    join
        genre_film_work as gfw
        on gfw.film_work_id = f.id
    join
        genre as g
        on g.id = gfw.genre_id
    group by
        gfw.film_work_id
    ),
persons as (
    select
        pfw.film_work_id as id,
        array_agg(p.full_name) filter (where pfw.role = 'director') directors_names,
        array_agg(p.full_name) filter (where pfw.role = 'actor') actors_names,
        array_agg(p.full_name) filter (where pfw.role = 'writer') writers_names,
        array_agg(json_build_object('id', p.id, 'full_name', p.full_name)) filter (where pfw.role = 'director') directors,
        array_agg(json_build_object('id', p.id, 'full_name', p.full_name)) filter (where pfw.role = 'actor') actors,
        array_agg(json_build_object('id', p.id, 'full_name', p.full_name)) filter (where pfw.role = 'writer') writers,
        max(greatest(pfw.created, p.modified)) as persons_modified
    from
    	ids_filter as f
    join
        person_film_work as pfw
        on pfw.film_work_id = f.id
    join
        person as p
        on p.id = pfw.person_id
    group by
        pfw.film_work_id
    )
select
    id,
    rating as imdb_rating,
    coalesce(genres, array[]::json[]) as genres,
    title,
    description,
    coalesce(directors_names, array[]::text[]) as directors_names,
    coalesce(actors_names, array[]::text[]) as actors_names,
    coalesce(writers_names, array[]::text[]) as writers_names,
    coalesce(directors, array[]::json[]) as directors,
    coalesce(actors, array[]::json[]) as actors,
    coalesce(writers, array[]::json[]) as writers,
    greatest(genres_modified, persons_modified, fw.modified)::varchar as modified
from
	ids_filter as f
join
    film_work as fw
    using(id)
left join
    genres as g
    using(id)
left join
    persons as p
    using(id)
order by
	modified
;