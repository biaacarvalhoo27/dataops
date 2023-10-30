SELECT 'CREATE DATABASE airflow'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='airflow')\gexec

CREATE USER airflow WITH PASSWORD 'airflow';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;

GRANT ALL ON SCHEMA public TO airflow;

SELECT 'CREATE DATABASE metabase'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='metabase')\gexec

SELECT 'CREATE DATABASE dmlops'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname='dmlops')\gexec

CREATE USER dmlops WITH PASSWORD 'dmlops';
GRANT ALL PRIVILEGES ON DATABASE dmlops TO dmlops;

GRANT ALL ON SCHEMA public TO dmlops;