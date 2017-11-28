drop table if exists files;
create table files (
    id integer not null primary key,
    path text not null,
    country varchar(2) not null,
    radar text not null,
    ftype text not null,
    angle float,
    ts text not null,
    quantities integer,
    ts_extra float
);
