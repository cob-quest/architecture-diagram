# diagram.py
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2,ElasticKubernetesService
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB, APIGateway
from diagrams.aws.network import VPC
from diagrams.onprem.iac import Terraform
from diagrams.onprem.ci import GitlabCI
from diagrams.aws.storage import S3

# from diagrams.aws.mobile import Amplify
from diagrams.k8s.network import Service



with Diagram("architecture", show=True, direction="TB"):
    ci_pipeline = GitlabCI("CI pipeline")
    container_registry = GitlabCI("Gitlab Container Registry")
    terraform_repo = Terraform("Infra as code")
    remote_state = S3("Remote state")



    with Cluster("AWS VPC"):

        api_gw = APIGateway("Api Gateway")
        eks = ElasticKubernetesService("EKS")
        for i in range(1,4):
            with Cluster("Private Subnet" + str(i)):

                with Cluster("EKS Cluster" + str(i)):

                    with Cluster("Frontend Services"+str(i)):
                        auth_service = Service("authsvc"+str(i))
                        frontend_service = Service("frontend"+str(i))
                        frontend_service - auth_service 
                    
                    with Cluster("Backend Services"+str(i)):
                        grading_service = Service("gradesvc"+str(i))
                        deployment_service = Service("deploymentsvc"+str(i))
            

                rds = RDS("database") 



                api_gw >> frontend_service

            
            grading_service >> rds
            frontend_service >> rds
            auth_service >> rds
    container_registry >> eks
    ci_pipeline - terraform_repo - remote_state
