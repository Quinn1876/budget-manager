BEGIN;
CREATE TABLE public.account
(
    account_number character varying(20) NOT NULL,
    account_type character varying(20) NOT NULL,
    owner text DEFAULT 'Quinn',
    account_name text DEFAULT '',
    initial_balance numeric NOT NULL DEFAULT 0,
    PRIMARY KEY (account_number)
);

ALTER TABLE IF EXISTS public.transactions
    ADD CONSTRAINT account_reference FOREIGN KEY (account_number)
    REFERENCES public.account (account_number) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION
    NOT VALID;
END;
