CREATE SEQUENCE pedidos_pedidoid_seq;
CREATE TABLE pedidos
(
    tipo_de_pizza character varying COLLATE pg_catalog."default",
    cantidad_de_pizza integer,
    tamano_de_pizza integer,
    fecha_de_pedido timestamp without time zone,
    usuarioid integer,
    pedidoid integer NOT NULL DEFAULT nextval('pedidos_pedidoid_seq'::regclass),
    CONSTRAINT "idKey" FOREIGN KEY (usuarioid)
        REFERENCES usuarios (usuarioid) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        NOT VALID
)