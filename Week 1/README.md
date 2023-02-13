## Homework 1 Docker and SQL

The homework is being completed on Ubuntu 22.10 installed as a virtual machine via Oracle VM VirtualBox.
___
### Question 1. Knowing docker tags
Which tag has the following text? - *Write the image ID to the file*

__Solution__:
The key command is

```sudo docker --help build```

In the appeared list of parameters the required text has `--iidfile string` parameter.

The script file [knowing_docker_tags.sh](https://github.com/Katrindenek/DE-Zoomcamp-Homework/blob/4f018ae8d649179336cb8311d842c27cba8ef3a3/Week%201/knowing_docker_tags.sh) has been used to get a line containing the required text for this task.
___
### Question 2. Understanding docker first run 

Run docker with the python:3.9 image in an interactive mode and the entrypoint of bash.
Now check the python modules that are installed ( use pip list). 
How many python packages/modules are installed?

__Solution__:
The [Dockerfile](https://github.com/Katrindenek/DE-Zoomcamp-Homework/blob/a6480bf2426c7031bd092e6750d370c073988740/Week%201/Dockerfile) contains the following code

```
FROM python:3.9

WORKDIR /app
COPY understanding_docker_first_run.sh understanding_docker_first_run.sh

ENTRYPOINT ["bash" , "./understanding_docker_first_run.sh"]
```
where [the bash script](https://github.com/Katrindenek/DE-Zoomcamp-Homework/blob/4db37c6cf250420f63867bf43e8c0124a69e31f6/Week%201/understanding_docker_first_run.sh) executes `pip list` command in the bash entrypoint.

Using the following commands in the Terminal we will get the list of python modules installed:
```
sudo docker build -t hw:2 .
sudo docker run -it hw:2
```
___
For the next tasks [the docker container](https://github.com/Katrindenek/DE-Zoomcamp-Homework/blob/77987eed86c9935844dfcc77eeba60b760ee5567/Week%201/docker-compose.yaml) was created and started using the following command in the Terminal from the same directory.
```
sudo docker-compose up -d
```

The analyzed dataset is a data of the green taxi trips in [New York City](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page). It is loaded to the Postgres database by the commands
```
URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-01.csv.gz"

python3 ingest_data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=green_taxi_trips \
  --url=${URL}
```

Additionally, the zones dataset was downloaded:
```
URL="https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv"

python3 ingest_data.py \
  --user=root \
  --password=root \
  --host=localhost \
  --port=5432 \
  --db=ny_taxi \
  --table_name=zones \
  --url=${URL}
```

The Python script [`ingest_data.py`](https://github.com/Katrindenek/DE-Zoomcamp-Homework/blob/171ec4afa1976866bab49c55cb248e2e309c4f83/Week%201/ingest_data.py) is doing sort of an ETL process for the data.
___
### Question 3. Count records

How many taxi trips were totally made on January 15?

__Solution__:
```
SELECT
	COUNT(*)
FROM green_taxi_trips
WHERE
	lpep_pickup_datetime::DATE = '2019-01-15'
	AND lpep_dropoff_datetime::DATE = '2019-01-15';
```
___
### Question 4. Largest trip for each day

Which was the day with the largest trip distance?

__Solution__:
```
SELECT
	lpep_pickup_datetime::DATE
FROM green_taxi_trips
WHERE
	trip_distance = (SELECT MAX(trip_distance)
			 FROM green_taxi_trips);
```
___
### Question 5. The number of passengers

In 2019-01-01 how many trips had 2 and 3 passengers?

__Solution__:
```
SELECT
	passenger_count,
	COUNT(*) AS number_of_passengers
FROM green_taxi_trips
WHERE
	lpep_pickup_datetime::DATE = '2019-01-01' 
	AND passenger_count BETWEEN 2 AND 3
GROUP BY passenger_count;
```
___
### Question 6. Largest tip

For the passengers picked up in the Astoria Zone which was the drop off zone that had the largest tip? We want the name of the zone, not the id.

__Solution__:
```
WITH astoria_pickup_trips AS (
	SELECT
		puz."Zone" AS pickup_zone,
		doz."Zone" AS dropoff_zone,
		trips.tip_amount
	FROM 
		green_taxi_trips trips
		LEFT JOIN zones puz
		ON trips."PULocationID" = puz."LocationID"
		LEFT JOIN zones doz
		ON trips."DOLocationID" = doz."LocationID"
	WHERE
		puz."Zone" = 'Astoria'
)

SELECT
	pickup_zone,
	dropoff_zone
FROM 
	astoria_pickup_trips
WHERE
	tip_amount = (SELECT MAX(tip_amount)
		      FROM astoria_pickup_trips);
```
