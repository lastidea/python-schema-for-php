drop table if exists schema;
create table schema (
  'id' integer primary key autoincrement,
  'title' text not null,
  'url' text not null,
  'success_return' text not null,
  'success_or_not' integer default 0,
  'type' integer default 0,
  'schema_time' integer default 0,
  'add_time' integer default 0,
  'run_time' integer default 0,
  'unit' integer default 0,
  'status' integer default 0,
  'text' text not null
);

drop table if exists schema_log;
create table schema_log (
  'id' integer primary key autoincrement,
  'success_return' text not null,
  'success_or_not' integer not null,
  'schema_id' integer default 0,
  'run_time' integer default 0
);