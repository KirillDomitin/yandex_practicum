set search_path to content;


select
    id,
    name,
    modified::varchar as modified
from
    genre
where
    modified > '{genres}'::timestamptz
;