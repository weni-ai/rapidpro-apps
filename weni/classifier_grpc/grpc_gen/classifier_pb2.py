# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: weni/classifier_grpc/grpc_gen/classifier.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='weni/classifier_grpc/grpc_gen/classifier.proto',
  package='weni.rapidpro.classifier',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n.weni/classifier_grpc/grpc_gen/classifier.proto\x12\x18weni.rapidpro.classifier\"[\n\x15\x43lassifierListRequest\x12\x10\n\x08org_uuid\x18\x01 \x01(\t\x12\x1c\n\x0f\x63lassifier_type\x18\x02 \x01(\tH\x00\x88\x01\x01\x42\x12\n\x10_classifier_type\"W\n\nClassifier\x12\x0c\n\x04uuid\x18\x01 \x01(\t\x12\x17\n\x0f\x63lassifier_type\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x04 \x01(\t\"q\n\x17\x43lassifierCreateRequest\x12\x0b\n\x03org\x18\x01 \x01(\t\x12\x0c\n\x04user\x18\x02 \x01(\t\x12\x17\n\x0f\x63lassifier_type\x18\x04 \x01(\t\x12\x0c\n\x04name\x18\x05 \x01(\t\x12\x14\n\x0c\x61\x63\x63\x65ss_token\x18\x06 \x01(\t2\xde\x01\n\x14\x43lassifierController\x12\x63\n\x06\x43reate\x12\x31.weni.rapidpro.classifier.ClassifierCreateRequest\x1a$.weni.rapidpro.classifier.Classifier\"\x00\x12\x61\n\x04List\x12/.weni.rapidpro.classifier.ClassifierListRequest\x1a$.weni.rapidpro.classifier.Classifier\"\x00\x30\x01\x62\x06proto3'
)




_CLASSIFIERLISTREQUEST = _descriptor.Descriptor(
  name='ClassifierListRequest',
  full_name='weni.rapidpro.classifier.ClassifierListRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='org_uuid', full_name='weni.rapidpro.classifier.ClassifierListRequest.org_uuid', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='classifier_type', full_name='weni.rapidpro.classifier.ClassifierListRequest.classifier_type', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='_classifier_type', full_name='weni.rapidpro.classifier.ClassifierListRequest._classifier_type',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=76,
  serialized_end=167,
)


_CLASSIFIER = _descriptor.Descriptor(
  name='Classifier',
  full_name='weni.rapidpro.classifier.Classifier',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='uuid', full_name='weni.rapidpro.classifier.Classifier.uuid', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='classifier_type', full_name='weni.rapidpro.classifier.Classifier.classifier_type', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='weni.rapidpro.classifier.Classifier.name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='access_token', full_name='weni.rapidpro.classifier.Classifier.access_token', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=169,
  serialized_end=256,
)


_CLASSIFIERCREATEREQUEST = _descriptor.Descriptor(
  name='ClassifierCreateRequest',
  full_name='weni.rapidpro.classifier.ClassifierCreateRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='org', full_name='weni.rapidpro.classifier.ClassifierCreateRequest.org', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='user', full_name='weni.rapidpro.classifier.ClassifierCreateRequest.user', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='classifier_type', full_name='weni.rapidpro.classifier.ClassifierCreateRequest.classifier_type', index=2,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='name', full_name='weni.rapidpro.classifier.ClassifierCreateRequest.name', index=3,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='access_token', full_name='weni.rapidpro.classifier.ClassifierCreateRequest.access_token', index=4,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=258,
  serialized_end=371,
)

_CLASSIFIERLISTREQUEST.oneofs_by_name['_classifier_type'].fields.append(
  _CLASSIFIERLISTREQUEST.fields_by_name['classifier_type'])
_CLASSIFIERLISTREQUEST.fields_by_name['classifier_type'].containing_oneof = _CLASSIFIERLISTREQUEST.oneofs_by_name['_classifier_type']
DESCRIPTOR.message_types_by_name['ClassifierListRequest'] = _CLASSIFIERLISTREQUEST
DESCRIPTOR.message_types_by_name['Classifier'] = _CLASSIFIER
DESCRIPTOR.message_types_by_name['ClassifierCreateRequest'] = _CLASSIFIERCREATEREQUEST
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ClassifierListRequest = _reflection.GeneratedProtocolMessageType('ClassifierListRequest', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFIERLISTREQUEST,
  '__module__' : 'weni.classifier_grpc.grpc_gen.classifier_pb2'
  # @@protoc_insertion_point(class_scope:weni.rapidpro.classifier.ClassifierListRequest)
  })
_sym_db.RegisterMessage(ClassifierListRequest)

Classifier = _reflection.GeneratedProtocolMessageType('Classifier', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFIER,
  '__module__' : 'weni.classifier_grpc.grpc_gen.classifier_pb2'
  # @@protoc_insertion_point(class_scope:weni.rapidpro.classifier.Classifier)
  })
_sym_db.RegisterMessage(Classifier)

ClassifierCreateRequest = _reflection.GeneratedProtocolMessageType('ClassifierCreateRequest', (_message.Message,), {
  'DESCRIPTOR' : _CLASSIFIERCREATEREQUEST,
  '__module__' : 'weni.classifier_grpc.grpc_gen.classifier_pb2'
  # @@protoc_insertion_point(class_scope:weni.rapidpro.classifier.ClassifierCreateRequest)
  })
_sym_db.RegisterMessage(ClassifierCreateRequest)



_CLASSIFIERCONTROLLER = _descriptor.ServiceDescriptor(
  name='ClassifierController',
  full_name='weni.rapidpro.classifier.ClassifierController',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=374,
  serialized_end=596,
  methods=[
  _descriptor.MethodDescriptor(
    name='Create',
    full_name='weni.rapidpro.classifier.ClassifierController.Create',
    index=0,
    containing_service=None,
    input_type=_CLASSIFIERCREATEREQUEST,
    output_type=_CLASSIFIER,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='List',
    full_name='weni.rapidpro.classifier.ClassifierController.List',
    index=1,
    containing_service=None,
    input_type=_CLASSIFIERLISTREQUEST,
    output_type=_CLASSIFIER,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_CLASSIFIERCONTROLLER)

DESCRIPTOR.services_by_name['ClassifierController'] = _CLASSIFIERCONTROLLER

# @@protoc_insertion_point(module_scope)
