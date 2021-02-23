from weni.user_grpc.grpc_gen import user_pb2_grpc

from weni.user_grpc.services import UserService


def grpc_handlers(server):
    user_pb2_grpc.add_UserControllerServicer_to_server(UserService.as_servicer(), server)