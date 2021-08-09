# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from weni.grpc.classifier.grpc_gen import classifier_pb2 as weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2


class ClassifierControllerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Create = channel.unary_unary(
                '/weni.rapidpro.classifier.ClassifierController/Create',
                request_serializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierCreateRequest.SerializeToString,
                response_deserializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.Classifier.FromString,
                )
        self.Retrieve = channel.unary_unary(
                '/weni.rapidpro.classifier.ClassifierController/Retrieve',
                request_serializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierRetrieveRequest.SerializeToString,
                response_deserializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.Classifier.FromString,
                )
        self.Destroy = channel.unary_unary(
                '/weni.rapidpro.classifier.ClassifierController/Destroy',
                request_serializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierDestroyRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.List = channel.unary_stream(
                '/weni.rapidpro.classifier.ClassifierController/List',
                request_serializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierListRequest.SerializeToString,
                response_deserializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.Classifier.FromString,
                )


class ClassifierControllerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Create(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Retrieve(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Destroy(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def List(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ClassifierControllerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Create': grpc.unary_unary_rpc_method_handler(
                    servicer.Create,
                    request_deserializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierCreateRequest.FromString,
                    response_serializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.Classifier.SerializeToString,
            ),
            'Retrieve': grpc.unary_unary_rpc_method_handler(
                    servicer.Retrieve,
                    request_deserializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierRetrieveRequest.FromString,
                    response_serializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.Classifier.SerializeToString,
            ),
            'Destroy': grpc.unary_unary_rpc_method_handler(
                    servicer.Destroy,
                    request_deserializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierDestroyRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'List': grpc.unary_stream_rpc_method_handler(
                    servicer.List,
                    request_deserializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierListRequest.FromString,
                    response_serializer=weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.Classifier.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'weni.rapidpro.classifier.ClassifierController', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ClassifierController(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Create(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/weni.rapidpro.classifier.ClassifierController/Create',
            weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierCreateRequest.SerializeToString,
            weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.Classifier.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Retrieve(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/weni.rapidpro.classifier.ClassifierController/Retrieve',
            weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierRetrieveRequest.SerializeToString,
            weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.Classifier.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Destroy(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/weni.rapidpro.classifier.ClassifierController/Destroy',
            weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierDestroyRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def List(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/weni.rapidpro.classifier.ClassifierController/List',
            weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.ClassifierListRequest.SerializeToString,
            weni_dot_grpc_dot_classifier_dot_grpc__gen_dot_classifier__pb2.Classifier.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
