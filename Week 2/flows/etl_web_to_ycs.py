from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_aws.s3 import S3Bucket


@task(retries=3)
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into pandas DataFrame"""

    df = pd.read_csv(dataset_url)
    return df


@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fix datetime type issues"""
    datetime_columns = df.columns[df.columns.str.contains('datetime')]
    print(f"Discovered {len(datetime_columns)} datetime columns")

    for column in datetime_columns:
        df[column] = pd.to_datetime(df[column])
        print(f"The column {column}'s type is {df[column].dtype}")

    print("Total rows:", len(df))
    return df


@task()
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""
    #path = Path(f"./data/{color}/{dataset_file}.parquet")
    #df.to_parquet(path, compression="gzip")
    path = Path(f"../data/{color}/{dataset_file}.parquet")
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True)   
    df.to_parquet(path, compression="gzip")
    return path


@task()
def write_ycs(path: Path) -> None:
    """Upload local parquet file to Yandex Object Storage"""
    s3_bucket_block = S3Bucket.load("zoom-ycs")
    s3_bucket_block.upload_from_path(from_path=path, to_path=path)
    return


@flow()
def etl_web_to_ycs(year: int, month: int, color: str) -> None:
    """The main ETL function"""
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"

    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    write_ycs(path)

@flow()
def etl_parent_flow(
    months: list[int] = [1, 2], year: int = 2021, color: str = "yellow"
):
    for month in months:
        etl_web_to_ycs(year, month, color)

if __name__ == "__main__":
    months = [1, 2, 3]
    etl_parent_flow(months=months)