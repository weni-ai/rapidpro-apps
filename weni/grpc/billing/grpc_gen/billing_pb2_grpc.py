# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from weni.grpc.billing.grpc_gen import billing_pb2 as weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2


class BillingStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Total = channel.unary_unary(
                '/weni.rapidpro.billing.Billing/Total',
                request_serializer=weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.BillingRequest.SerializeToString,
                response_deserializer=weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.BillingResponse.FromString,
                )
        self.Detailed = channel.unary_stream(
                '/weni.rapidpro.billing.Billing/Detailed',
                request_serializer=weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.BillingRequest.SerializeToString,
                response_deserializer=weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.ActiveContactDetail.FromString,
                )


class BillingServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Total(self, request, context):
        """Get the total or active contacts in a time range
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Detailed(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BillingServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Total': grpc.unary_unary_rpc_method_handler(
                    servicer.Total,
                    request_deserializer=weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.BillingRequest.FromString,
                    response_serializer=weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.BillingResponse.SerializeToString,
            ),
            'Detailed': grpc.unary_stream_rpc_method_handler(
                    servicer.Detailed,
                    request_deserializer=weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.BillingRequest.FromString,
                    response_serializer=weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.ActiveContactDetail.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'weni.rapidpro.billing.Billing', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Billing(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Total(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/weni.rapidpro.billing.Billing/Total',
            weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.BillingRequest.SerializeToString,
            weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.BillingResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Detailed(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/weni.rapidpro.billing.Billing/Detailed',
            weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.BillingRequest.SerializeToString,
            weni_dot_grpc_dot_billing_dot_grpc__gen_dot_billing__pb2.ActiveContactDetail.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
