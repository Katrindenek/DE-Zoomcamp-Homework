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

#### Solution:

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

### Question 3. Loading data to BigQuery 

Using `etl_gcs_to_bq.py` as a starting point, modify the script for extracting data from GCS and loading it into BigQuery. This new script should not fill or remove rows with missing values. (The script is really just doing the E and L parts of ETL).

The main flow should print the total number of rows processed by the script. Set the flow decorator to log the print statement.

Parametrize the entrypoint flow to accept a list of months, a year, and a taxi color. 

Make any other necessary changes to the code for it to function as required.

Create a deployment for this flow to run in a local subprocess with local flow code storage (the defaults).

Make sure you have the parquet data files for Yellow taxi data for Feb. 2019 and March 2019 loaded in GCS. Run your deployment to append this data to your BiqQuery table. How many rows did your flow code process?

- 14,851,920
- 12,282,990
- 27,235,753
- 11,338,483

#### Solution.

Unfortunately, I could not use Google Cloud. [The Yandex Query](https://cloud.yandex.com/en/docs/query/concepts/), as I understood, doesn't really store data but takes them from the Object Storage via connections. It didn't make sense to me to work on anything like "etl_ycs_to_yq.py" Python script, so I loaded the required data into the Object Storage using the described earlier script, connected to it with Yandex Query UI and completed the following query:
```
SELECT
    COUNT(*)
FROM
    (SELECT 
        *
    FROM
        `de-zoomcamp-prefect`.`data/yellow/yellow_tripdata_2019-02.csv`
    WITH (
        format='csv_with_names',
        SCHEMA 
        (
            `VendorID` double,
            `tpep_pickup_datetime` Datetime,
            `tpep_dropoff_datetime` Datetime,
            `passenger_count` Double,
            `trip_distance` Double,
            `RatecodeID` Double,
            `store_and_fwd_flag` String,
            `PULocationID` Int64,
            `DOLocationID` Int64,
            `payment_type` Double,
            `fare_amount` Double,
            `extra` Double,
            `mta_tax` Double,
            `tip_amount` Double,
            `tolls_amount` Double,
            `improvement_surcharge` Double,
            `total_amount` Double,
            `congestion_surcharge` Double
        )
    )
    UNION ALL
    SELECT 
        *
    FROM
        `de-zoomcamp-prefect`.`data/yellow/yellow_tripdata_2019-03.csv`
    WITH (
        format='csv_with_names',
        SCHEMA 
        (
            `VendorID` double,
            `tpep_pickup_datetime` Datetime,
            `tpep_dropoff_datetime` Datetime,
            `passenger_count` Double,
            `trip_distance` Double,
            `RatecodeID` Double,
            `store_and_fwd_flag` String,
            `PULocationID` Int64,
            `DOLocationID` Int64,
            `payment_type` Double,
            `fare_amount` Double,
            `extra` Double,
            `mta_tax` Double,
            `tip_amount` Double,
            `tolls_amount` Double,
            `improvement_surcharge` Double,
            `total_amount` Double,
            `congestion_surcharge` Double
        )
    )
);
```

As you can see, the files actually have the `.csv` format. That's because [Yandex Query](https://cloud.yandex.com/en/docs/query/sources-and-sinks/formats#parquet) currently doesn't support `.parquet` files with size more than 50 MB. So, I also had to modify my `etl_web_to_ycs.py` script a bit and create another temporary deployment for that purpose... Perhaps, it is worth adding the file format as another parameter to the current deployment to be able to resolve such issues faster.

The answer is: __14,851,920__.

### Question 4. Github Storage Block

Using the `web_to_gcs` script from the videos as a guide, you want to store your flow code in a GitHub repository for collaboration with your team. Prefect can look in the GitHub repo to find your flow code and read it. Create a GitHub storage block from the UI or in Python code and use that in your Deployment instead of storing your flow code locally or baking your flow code into a Docker image. 

Note that you will have to push your code to GitHub, Prefect will not push it for you.

Run your deployment in a local subprocess (the default if you don’t specify an infrastructure). Use the Green taxi data for the month of November 2020.

How many rows were processed by the script?

- 88,019
- 192,297
- 88,605
- 190,225

### Solution.

The GitHub block "zoom-github" was created via Prefect Orion UI referring to the current repository. The following command created a deployment named "etl_github":
```
prefect deployment build "Week 2/flows/etl_web_to_ycs.py":etl_parent_flow --name etl_github -sb github/zoom-github -a
```

The deployment was run by the command
```
prefect deployment run etl-parent-flow/etl_github -p "months=[11]" -p "year=2020" -p "color=green"
```

The answer is: __88,605__.

### Question 5. Email or Slack notifications

Q5. It’s often helpful to be notified when something with your dataflow doesn’t work as planned. Choose one of the options below for creating email or slack notifications.

The hosted Prefect Cloud lets you avoid running your own server and has Automations that allow you to get notifications when certain events occur or don’t occur. 

Create a free forever Prefect Cloud account at app.prefect.cloud and connect your workspace to it following the steps in the UI when you sign up. 

Set up an Automation that will send yourself an email when a flow run completes. Run the deployment used in Q4 for the Green taxi data for April 2019. Check your email to see the notification.

Alternatively, use a Prefect Cloud Automation or a self-hosted Orion server Notification to get notifications in a Slack workspace via an incoming webhook. 

Join my temporary Slack workspace with [this link](https://join.slack.com/t/temp-notify/shared_invite/zt-1odklt4wh-hH~b89HN8MjMrPGEaOlxIw). 400 people can use this link and it expires in 90 days. 

In the Prefect Cloud UI create an [Automation](https://docs.prefect.io/ui/automations) or in the Prefect Orion UI create a [Notification](https://docs.prefect.io/ui/notifications/) to send a Slack message when a flow run enters a Completed state. Here is the Webhook URL to use: https://hooks.slack.com/services/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

Test the functionality.

Alternatively, you can grab the webhook URL from your own Slack workspace and Slack App that you create. 


How many rows were processed by the script?

- `125,268`
- `377,922`
- `728,390`
- `514,392`

#### Solution.

I created my own Slack workspace and Slack App to complete this task. I generated a Webhook URL in the Slack app and added it to Notifications tab in Prefect Orion UI. Now, if a run of any flow with any tag enters any state, I get a notification.

<img src="https://github.com/Katrindenek/DE-Zoomcamp-Homework/blob/ba097935e8d2c694833a52a03ff665f342431378/Week%202/pictures/slack_notification.png" width="400">

The answer is __514,392__.

### Question 6. Secrets

Prefect Secret blocks provide secure, encrypted storage in the database and obfuscation in the UI. Create a secret block in the UI that stores a fake 10-digit password to connect to a third-party service. Once you’ve created your block in the UI, how many characters are shown as asterisks (*) on the next page of the UI?

- 5
- 6
- 8
- 10

#### Solution.

Prefect allows storing encrypted credentials and use them in code without exposing such vulnerable data.

The answer is __8__.
