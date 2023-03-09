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
As a transform part, the script changes a type for the datetime columns, as they are `object` by default. 

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

### Question 2. Scheduling with Cron

Cron is a common scheduling specification for workflows. 

Using the flow in `etl_web_to_gcs.py`, create a deployment to run on the first of every month at 5am UTC. What’s the cron schedule for that?

- `0 5 1 * *`
- `0 0 5 1 *`
- `5 * 1 0 *`
- `* * 5 1 0`

The answer is __`0 5 1 * *`__. 

There are several ways to set up a schedule in Prefect.

1. The easiest one is using the UI. Go to Prefect Orion > Deployments > Click on the deployment which you want to schedule > Click 'Schedule' in the right menu. In the popped up window, you can choose a schedule type. At the moment, CRON seems to be the most convenient and universal one, though looks scary at the beginning. [Online converter](https://crontab.cronhub.io/) can help to generate and explain the CRON expression.

2. Another way is to use CLI when building the deployment. For the script `etl_web_to_ycs.py` it'd be
```
prefect deployment build etl_web_to_ycs.py:etl_parent_flow -n etl_cli --cron "0 5 1 * *" -a
```
where `-n` is a flag for a name of the deployment, `--cron` - a cron expression flag, `-a` stands for "apply".

3. When you build a deployment as shown just above, Prefect creates a file named `etl_parent_flow-deployment.yaml`. It is a metadata file where you can change many of the deployment parameters, including the schedule. So, another way to do the task is to create or change the .yaml file and apply it with a command:
```
prefect deployment apply etl_parent_flow-deployment.yaml
```

4. The two previous approaches don't really suit the way how my flow was realised because the deployment was built and applied inside `docker_deploy.py` script. In this case, the schedule can be specified as an argument as following:
```
docker_dep = Deployment.build_from_flow(
    flow=etl_parent_flow,
    name='docker-flow',
    infrastructure=docker_block,
    schedule={"cron": "0 5 1 * *"}
)
```
