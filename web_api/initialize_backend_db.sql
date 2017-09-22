create database backend_db ENCODING 'UTF8' LC_COLLATE 'C' LC_CTYPE 'C' TEMPLATE template0;
\c backend_db;

CREATE COLLATION "ja_JP.utf8" (LOCALE = 'ja_JP.UTF-8');
CREATE USER docker PASSWORD 'docker' ;

/* a table to save knp analysis result */
create table knp_result (
    text_id varchar(64),
    sentence_index  integer,
    task_id varchar(64),
    knp_result TEXT,
    status BOOLEAN,
    created_at  timestamp with time zone    not null    DEFAULT now(),
    PRIMARY KEY (text_id, sentence_index, task_id)
    );
CREATE INDEX idx_knp_result_01 ON knp_result (text_id);
CREATE INDEX idx_knp_result_02 ON knp_result (task_id);
CREATE INDEX idx_knp_result_03 ON knp_result (status);
ALTER TABLE public.knp_result OWNER TO docker;
GRANT ALL ON TABLE public.knp_result TO docker;


/* a tbale to manage task status */
create table task_status(
    task_id varchar(64)    primary key,
    task_status  varchar(32),
    description varchar(128),
    created_at  timestamp with time zone    not null    DEFAULT now(),
    updated_at  timestamp with time zone    not null    DEFAULT now()
);
ALTER TABLE public.task_status OWNER TO docker;
GRANT ALL ON TABLE public.task_status TO docker;