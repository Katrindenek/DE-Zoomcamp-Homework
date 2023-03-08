## Homework 2 Workflow orchestration with Prefect

The homework is being completed on Ubuntu 22.10 installed as a virtual machine via Oracle VM VirtualBox.

The course implies using GCP and BigQuery, but due to several problems with Google Cloud, I used Yandex Cloud Object Storage and Yandex Query.

### Question 1. Load January 2020 data

Using the `etl_web_to_gcs.py` flow that loads taxi data into GCS as a guide, create a flow that loads the green taxi CSV dataset for January 2020 into GCS and run it. Look at the logs to find out how many rows the dataset has.

How many rows does that dataset have?

* 447,770
* 766,792
* 299,234
* 822,132

#### Solution:

The Python script `etl_web_to_ycs.py` containing all the ETL logic. It takes the parameters `months`, `year` and `color`, downloads the corresponding NY taxi dataset and loads to the Object Storage.
As a transform part, the script changes a type for the datetime columns as they are `object` by default. 

The connection to the Yandex Object Storage is done using the Prefect UI. The AWS S3 block is created and set up to connect to the Object Storage.

Another block created in Prefect is a Docker container. The script is packed and loaded into a [Docker Hub](https://hub.docker.com/r/katrindenek/prefect/tags).
The Python script `docker_deploy.py` creates a deployment upon the Docker block.

Finally, starting a Prefect agent locally 
```
prefect agent start  --work-queue "default"
```
we can start running the flow with the following command:
```
prefect deployment run etl-parent-flow/docker-flow -p "months=[1]" -p "year=2020" -p "color=green"
```
where the required parameters are specified.

The size of the loaded dataset is __447,770 rows__.
