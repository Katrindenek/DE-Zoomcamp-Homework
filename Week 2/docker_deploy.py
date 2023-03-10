from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer
from flows.etl_web_to_ycs import etl_parent_flow

docker_block = DockerContainer.load("zoom")

docker_dep = Deployment.build_from_flow(
    flow=etl_parent_flow,
    name='docker-flow',
    infrastructure=docker_block,
    schedule={"cron": "0 5 1 * *"}
)

if __name__ == "__main__":
    docker_dep.apply()