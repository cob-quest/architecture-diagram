# diagram.py
from diagrams import Diagram, Cluster
from diagrams.aws.compute import ElasticKubernetesService
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB, ALB, Route53, NATGateway
from diagrams.aws.network import VPC, APIGateway
from diagrams.onprem.iac import Terraform
from diagrams.onprem.ci import GitlabCI
from diagrams.aws.storage import S3
from diagrams.custom import Custom
# from diagrams.aws.mobile import Amplify
from diagrams.k8s.network import Service, Ing
from diagrams.k8s.compute import Cronjob



with Diagram("architecture", show=False, direction="TB"):
    ci_pipeline = GitlabCI("CI pipeline")
    container_registry = GitlabCI("Gitlab Container Registry")
    terraform_repo = Terraform("Infra as code")
    remote_state = S3("Remote state")
    users = Custom("Users","custom/users.png") 

    with Cluster("AWS Cloud"):
        apigw = APIGateway("API Gateway")
        with Cluster("AWS VPC"):

            alb = ALB("Application LoadBalancer")
            elb = ELB("Elastic LoadBalancer")
            eks = ElasticKubernetesService("EKS")
            natgws = []
            with Cluster("Public Subnet"):
                for i in range(1,4):
                    with Cluster("Subnet {}".format(i)):
                        natgw = NATGateway("Nat GW")
                        natgws.append(natgw)


            with Cluster("Private Subnet"):
                for i in range(1,4):
                    with Cluster("Subnet {}".format(i)):
                        rds = RDS("database") 



                            


                        with Cluster("EKS Assignment Node {}".format(i)):
                            assignment_ingress = Ing("k8 ingress")

                            with Cluster("DNS Service*"):
                                external_dns = Service("External DNS")
                            with Cluster("Assignment Services"):
                                grading_service = Service("gradesvc")
                                deploy_assignment_service = Service("deployAssignment")
                                cron_assignment_timer = Cronjob("assignmentTimer")

                            ## Connections
                            grading_service >> rds
                            assignment_ingress >> deploy_assignment_service
                            elb >> natgws[i-1] >> assignment_ingress
                            container_registry - deploy_assignment_service
                            cron_assignment_timer >> deploy_assignment_service
                            deploy_assignment_service >> grading_service


                        with Cluster("EKS Platform Node {}".format(i)):
                            platform_ingress = Ing("k8 ingress")
                            
                            
                            with Cluster("DNS Service*"):
                                external_dns = Service("External DNS")
                            with Cluster("Frontend Services"):
                                # auth_service = Service("authsvc")
                                frontend_service = Service("frontend")
                            with Cluster("Image Builder Services"):
                                # auth_service = Service("authsvc")
                                image_builder_service = Service("Image Builder")
                            
                            with Cluster("Process Engine Service"):
                                process_engine_service = Service("Process Engine")
                            
                            ## Connections
                            frontend_service >> process_engine_service
                            # process_engine_service - auth_service >> rds
                            platform_ingress >> frontend_service
                            alb >> natgws[i-1] >> platform_ingress
                            container_registry - image_builder_service
                            process_engine_service >> image_builder_service
                            process_engine_service >> grading_service
        
    
    container_registry >> eks
    grading_service - deploy_assignment_service
    ci_pipeline - terraform_repo - remote_state
    apigw >> alb
    apigw >> elb
    users >> apigw
