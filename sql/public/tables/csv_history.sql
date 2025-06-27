BEGIN;

CREATE TABLE IF NOT EXISTS public.csv_history
(
    id uuid NOT NULL,
    path text COLLATE pg_catalog."default" NOT NULL,
    datetime_added timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT csv_history_pkey PRIMARY KEY (id)
);

COMMENT ON TABLE public.csv_history
    IS 'History of the CSV Files that have been uploaded to the database. To prevent duplicate csv entries since the csvs don''t have the unique transaction IDs';
END;
