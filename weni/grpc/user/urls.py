from weni.protobuf.flows import user_pb2_grpc

from weni.grpc.user.services import UserPermissionService, UserService


def grpc_handlers(server):
    user_pb2_grpc.add_UserPermissionControllerServicer_to_server(UserPermissionService.as_servicer(), server)
    user_pb2_grpc.add_UserControllerServicer_to_server(UserService.as_servicer(), server)
