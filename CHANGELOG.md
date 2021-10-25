## [Unreleased]

## [1.0.2] - 2021-10-26
### Changed
- `weni-protobuffers` updated to 1.2.0

### Fixed
- Adjusted Org reference on WeniWebChatProtoSerializer (#72)

## [1.0.0] - 2021-10-06
### Published on PyPI

## [0.3.0] - 2021-10-06
### Added
- `weni.grpc.channel`

### Changed
- The package now is built with Poetry
- Protocol Buffers now comes from `weni-protobuffers` as package dependency

### Fixed
- Org user_email and update return (#65)
- Type of BillingRequest.before and BillingRequest.after (#66)
- Set None as default value to the country field on template message endpoint (#68)
- Channel endpoint now returns UUID on Weni Web Chat (#69)

## [0.2.0] - 2021-08-23
### Added
- FlowRunAnalyticsEndpoint view
- Python Package files
- `weni.auth`
- GRPC modules:
  - `weni.grpc.core`
  - `weni.grpc.org`
  - `weni.grpc.flow`
  - `weni.grpc.user`
  - `weni.grpc.billing`
  - `weni.grpc.classifier`
- `weni.templates.context_processors.enable_weni_layout` context processor, to select page layout based on request's domain
- Converted to Python package with setuptools

### Removed
- weni.contacts_ext

## [0.1.0] - 2021-01-31 (First Release)
### Added
- weni.analytics_api
- weni.channel_stats
- weni.contacts_ext
- weni.utils
