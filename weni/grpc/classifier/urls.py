from weni.protobuf.flows import classifier_pb2_grpc
from weni.grpc.classifier.services import ClassifierService


def grpc_handlers(server):
    classifier_pb2_grpc.add_ClassifierControllerServicer_to_server(ClassifierService.as_servicer(), server)
