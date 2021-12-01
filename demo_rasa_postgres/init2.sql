CREATE TABLE direcciones
(
    nombre_de_via character varying(1000) COLLATE pg_catalog."default",
    numero_de_via character varying(10) COLLATE pg_catalog."default",
    numero_de_piso character varying(10) COLLATE pg_catalog."default",
    puerta character varying(10) COLLATE pg_catalog."default",
    usuarioid integer,
    tipo_de_via character varying(1000) COLLATE pg_catalog."default",
    codigo_postal character varying(5) COLLATE pg_catalog."default",
    CONSTRAINT "uniqueKey" UNIQUE (usuarioid),
    CONSTRAINT idkey FOREIGN KEY (usuarioid)
        REFERENCES usuarios (usuarioid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)