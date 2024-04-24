set search_path to content;


select
    id,
    full_name,
    modified::varchar as modified
from
    person
where
    modified > '{persons}'::timestamptz
;