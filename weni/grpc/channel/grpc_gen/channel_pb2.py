# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: weni/grpc/channel/grpc_gen/channel.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor.FileDescriptor(
    name="weni/grpc/channel/grpc_gen/channel.proto",
    package="weni.rapidpro.channel",
    syntax="proto3",
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n(weni/grpc/channel/grpc_gen/channel.proto\x12\x15weni.rapidpro.channel"H\n\x18WeniWebChatCreateRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04user\x18\x02 \x01(\t\x12\x10\n\x08\x62\x61se_url\x18\x03 \x01(\t"\x1b\n\x0bWeniWebChat\x12\x0c\n\x04uuid\x18\x01 \x01(\t2x\n\x15WeniWebChatController\x12_\n\x06\x43reate\x12/.weni.rapidpro.channel.WeniWebChatCreateRequest\x1a".weni.rapidpro.channel.WeniWebChat"\x00\x62\x06proto3',
)


_WENIWEBCHATCREATEREQUEST = _descriptor.Descriptor(
    name="WeniWebChatCreateRequest",
    full_name="weni.rapidpro.channel.WeniWebChatCreateRequest",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="name",
            full_name="weni.rapidpro.channel.WeniWebChatCreateRequest.name",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="user",
            full_name="weni.rapidpro.channel.WeniWebChatCreateRequest.user",
            index=1,
            number=2,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="base_url",
            full_name="weni.rapidpro.channel.WeniWebChatCreateRequest.base_url",
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=67,
    serialized_end=139,
)


_WENIWEBCHAT = _descriptor.Descriptor(
    name="WeniWebChat",
    full_name="weni.rapidpro.channel.WeniWebChat",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="uuid",
            full_name="weni.rapidpro.channel.WeniWebChat.uuid",
            index=0,
            number=1,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=141,
    serialized_end=168,
)

DESCRIPTOR.message_types_by_name["WeniWebChatCreateRequest"] = _WENIWEBCHATCREATEREQUEST
DESCRIPTOR.message_types_by_name["WeniWebChat"] = _WENIWEBCHAT
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

WeniWebChatCreateRequest = _reflection.GeneratedProtocolMessageType(
    "WeniWebChatCreateRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _WENIWEBCHATCREATEREQUEST,
        "__module__": "weni.grpc.channel.grpc_gen.channel_pb2"
        # @@protoc_insertion_point(class_scope:weni.rapidpro.channel.WeniWebChatCreateRequest)
    },
)
_sym_db.RegisterMessage(WeniWebChatCreateRequest)

WeniWebChat = _reflection.GeneratedProtocolMessageType(
    "WeniWebChat",
    (_message.Message,),
    {
        "DESCRIPTOR": _WENIWEBCHAT,
        "__module__": "weni.grpc.channel.grpc_gen.channel_pb2"
        # @@protoc_insertion_point(class_scope:weni.rapidpro.channel.WeniWebChat)
    },
)
_sym_db.RegisterMessage(WeniWebChat)


_WENIWEBCHATCONTROLLER = _descriptor.ServiceDescriptor(
    name="WeniWebChatController",
    full_name="weni.rapidpro.channel.WeniWebChatController",
    file=DESCRIPTOR,
    index=0,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
    serialized_start=170,
    serialized_end=290,
    methods=[
        _descriptor.MethodDescriptor(
            name="Create",
            full_name="weni.rapidpro.channel.WeniWebChatController.Create",
            index=0,
            containing_service=None,
            input_type=_WENIWEBCHATCREATEREQUEST,
            output_type=_WENIWEBCHAT,
            serialized_options=None,
            create_key=_descriptor._internal_create_key,
        ),
    ],
)
_sym_db.RegisterServiceDescriptor(_WENIWEBCHATCONTROLLER)

DESCRIPTOR.services_by_name["WeniWebChatController"] = _WENIWEBCHATCONTROLLER

# @@protoc_insertion_point(module_scope)