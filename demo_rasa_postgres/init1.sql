CREATE SEQUENCE usuarios_usuarioid_seq;
CREATE TABLE usuarios
(
    nombre character(1000) COLLATE pg_catalog."default",
    primer_apellido character(1000) COLLATE pg_catalog."default",
    segundo_apellido character(1000) COLLATE pg_catalog."default",
    usuarioid integer NOT NULL DEFAULT nextval('usuarios_usuarioid_seq'),
    CONSTRAINT usuarios_pkey PRIMARY KEY (usuarioid)
)