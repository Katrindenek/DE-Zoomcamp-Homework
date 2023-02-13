import pandas as pd
from sqlalchemy import create_engine
from time import time

import os
import argparse

def main(params):
    user = params.user
    password = params.password
    host = params.host 
    port = params.port 
    db = params.db
    table_name = params.table_name
    url = params.url

    # the backup files are gzipped, and it's important to keep the correct extension
    # for pandas to be able to open the file
    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'

    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = next(df_iter)
    process_date_types(df)

    df.head(0).to_sql(name=table_name, con=engine, if_exists='replace')
    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True:
        try:
            t_start = time()
            df = next(df_iter)
            process_date_types(df)

            df.to_sql(name=table_name, con=engine, if_exists='append')

            t_end = time()

            print("Inserted another chunk... Took %.3f seconds" % (t_end - t_start))
        except StopIteration:
            print("Finished ingesting data into the Postgres database")
            break


def process_date_types(df_data):
    datetime_columns = df_data.columns[df_data.columns.str.contains('datetime')]
    print(f"Discovered {len(datetime_columns)} datetime columns")

    for column in datetime_columns:
        df_data[column] = pd.to_datetime(df_data[column])
        print(f"The column {column}'s type is {df_data[column].dtype}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')

    parser.add_argument('--user', required=True, help='user name for postgres')
    parser.add_argument('--password', required=True, help='password for postgres')
    parser.add_argument('--host', required=True, help='host for postgres')
    parser.add_argument('--port', required=True, help='port for postgres')
    parser.add_argument('--db', required=True, help='database name for postgres')
    parser.add_argument('--table_name', required=True, help='name of the table where we will write the results to')
    parser.add_argument('--url', required=True, help='url of the csv file')

    args = parser.parse_args()

    main(args)
