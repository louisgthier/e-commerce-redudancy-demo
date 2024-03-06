FROM postgres:16.2

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_DB=ecommerce

COPY ./init.sql /docker-entrypoint-initdb.d/init.sql