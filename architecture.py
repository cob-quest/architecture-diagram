# diagram.py
from diagrams import Diagram, Cluster
from diagrams.aws.compute import ElasticKubernetesService
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB, ALB, Route53, NATGateway
from diagrams.aws.network import VPC
from diagrams.onprem.iac import Terraform
from diagrams.onprem.ci import GitlabCI
from diagrams.aws.storage import S3
from diagrams.custom import Custom
# from diagrams.aws.mobile import Amplify
from diagrams.k8s.network import Service, Ing




with Diagram("architecture", show=False, direction="TB"):
    ci_pipeline = GitlabCI("CI pipeline")
    container_registry = GitlabCI("Gitlab Container Registry")
    terraform_repo = Terraform("Infra as code")
    remote_state = S3("Remote state")
    users = Custom("Users","custom/users.png") 

    with Cluster("AWS Cloud"):

        r53 = Route53("DNS")
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


                        with Cluster("EKS Platform Node {}".format(i)):
                            platform_ingress = Ing("k8 ingress")
                            
                            
                            with Cluster("DNS Service"):
                                external_dns = Service("External DNS")
                            with Cluster("Frontend Services"):
                                auth_service = Service("authsvc")
                                frontend_service = Service("frontend")
                            
                            with Cluster("Backend Services"):
                                rest_backend_service = Service("Rest Backend")
                            
                            ## Connections
                            frontend_service - rest_backend_service  >> rds
                            rest_backend_service - auth_service >> rds
                            platform_ingress >> frontend_service
                            alb >> natgws[i-1] >> platform_ingress

                            


                        with Cluster("EKS Assignment Node {}".format(i)):
                            assignment_ingress = Ing("k8 ingress")

                            with Cluster("DNS Service"):
                                external_dns = Service("External DNS")
                            with Cluster("Backend Services"):

                                grading_service = Service("gradesvc")
                                assignment_service = Service("assignmentsvc")

                            ## Connections
                            grading_service >> rds
                            assignment_ingress >> assignment_service
                            elb >> natgws[i-1] >> assignment_ingress


        
      
    container_registry >> eks
    grading_service - assignment_service
    ci_pipeline - terraform_repo - remote_state
    r53 >> alb
    users >> r53
    users >> elb