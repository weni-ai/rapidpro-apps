from weni.user_grpc.grpc_gen import user_pb2_grpc

from weni.user_grpc.services import UserPermissionService


def grpc_handlers(server):
    user_pb2_grpc.add_UserPermissionControllerServicer_to_server(UserPermissionService.as_servicer(), server)
