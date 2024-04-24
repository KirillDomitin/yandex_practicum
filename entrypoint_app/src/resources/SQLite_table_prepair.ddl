-- film_work
---
select
    id,
    title,
    description,
    creation_date,
    rating,
    "type",
    created_at as created,
    updated_at as modified
from
    film_work
;
----
-- genre
---
select
    id,
    "name",
    description,
    created_at as created,
    updated_at as modified
from
    genre
;
----
-- person
---
select
    id,
    full_name,
    created_at as created,
    updated_at as modified
from
    person
;
----
-- genre_film_work
---
select
    id,
    film_work_id,
    genre_id,
    created_at as created
from
    genre_film_work
;
----
-- person_film_work
---
select
    id,
    film_work_id,
    person_id,
    role,
    created_at as created
from
    person_film_work
;