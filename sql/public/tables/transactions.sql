CREATE TABLE IF NOT EXISTS public.transactions
(
    account_number character varying(20) COLLATE pg_catalog."default" NOT NULL,
    date date NOT NULL,
    description_1 text COLLATE pg_catalog."default",
    description_2 text COLLATE pg_catalog."default",
    amount numeric NOT NULL,
    currency character(4) COLLATE pg_catalog."default" NOT NULL DEFAULT 'CAD$'::bpchar,
    transaction_id uuid NOT NULL,
    CONSTRAINT transactions_pkey PRIMARY KEY (transaction_id)
);
