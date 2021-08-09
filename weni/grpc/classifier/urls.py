from weni.classifier_grpc.grpc_gen import classifier_pb2_grpc
from weni.classifier_grpc.services import ClassifierService


def grpc_handlers(server):
    classifier_pb2_grpc.add_ClassifierControllerServicer_to_server(ClassifierService.as_servicer(), server)
