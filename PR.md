# Remove gRPC from rapidpro-apps

## What

This change removes gRPC from this repository. Nothing gRPC-related is left in the package, including handlers, tests, and dependencies.

- Deleted the entire `weni/grpc` package (apps, services, proto serializers, tests, and the `grpc` management command).
- Removed `djangogrpcframework`, `grpcio`, `protobuf`, and `grpcio-tools` from `pyproject.toml` and regenerated `poetry.lock`.
- Updated docs and ignore rules: dropped the gRPC development-patterns note from `README.md` and the proto/`*_pb2*` ignore entries from `.gitignore`.

The REST API still needed one helper that previously lived under gRPC. `SerializerMethodCharField` was moved from `weni/grpc/core/serializers.py` into `weni/serializers/fields.py` (and re-exported from `weni.serializers`). It is a `CharField` that reads through a serializer method (`get_{field_name}`), so it can be written on create and still return a derived value on read.

Internal REST serializers were updated to import shared fields from `weni.serializers` instead of `weni.grpc.core`:

- `weni/internal/classifier/serializers.py` — still uses `SerializerMethodCharField` for `access_token`
- `weni/internal/orgs/serializers.py` — `UserEmailRelatedField` for `modified_by`

The field implementation itself was not redesigned; it was copied as-is so classifier create/read behavior stays the same after gRPC is gone.

Host RapidPro settings that still list `weni.grpc.*` apps or gRPC handler hooks should be cleaned up separately, or Django will fail to import those modules.

## Why

gRPC is no longer used. Keeping `weni.grpc` and its libraries would leave unused code and a hard dependency on `grpcio` / protobuf in a package that only needs Django REST apps.

`SerializerMethodCharField` had to be relocated because the internal classifier serializer imported it from `weni.grpc.core`. Deleting gRPC without that move would break the REST classifier API on import, even though that endpoint is not gRPC. `UserEmailRelatedField` and `OrgUUIDRelatedField` already existed in `weni.serializers.fields`; this field was the only remaining piece the REST layer still pulled from the gRPC module.

Moving it into the shared serializers package decouples REST from gRPC so the unused stack can be removed without changing API contracts.
