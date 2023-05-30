## [Unreleased]

## [2.4.3] - 2023-05-30
- Removes the ticketer object from the queue.release() method
- Run black and flake8 in rp-apps

## [2.4.2] - 2023-05-18
- Filter active orgs to return statistics

## [2.4.1] - 2023-05-17
- Add external_api channel form in channel retrieve
- Release ticketer instance before delete queue
- Optimize search filter for active contacts

## [2.4.0] - 2023-05-03
- Add Project model to internal app
- Adjust Channel app to new project model
- Adjust Org app to new project model
- Adjust Users app to new project model

## [2.3.4] - 2023-04-27
- Update permission endpoint from User permission
- Update pre-commit config

## [2.3.3] - 2023-04-20
- Removing the internal ticketer from org serializer template
- Add agent permission in get_permissions method
- Add delete endpoint in external-services

## [2.3.2] - 2023-04-14
- Update globals endpoint to filter by org

## [2.3.0] - 2023-04-06
- Add endpoint allows the generic creation of an external service

## [2.2.0] - 2023-03-30
- Add endpoint that allows creating, retrieving, destroying and listing globals

## [2.1.3] - 2023-02-17
- Adjust the org field in the channel listing return
- Fix: does not create activities when updating the channel.config at whatsapp and whatsapp-cloud

## [2.1.2] - 2023-02-03
- Fix change the has_issues field to False, when create flow

## [2.1.1] - 2022-12-28
- Fix error with magic package usage

## [2.1.0] - 2022-12-27
- Add success org retrieve endpoint
- Create an internal client for the connect REST API
- Create new Django App from recent activity
- When creating a classifier syncs it synchronously

## [2.0.1] - 2022-12-27
- Feature: Add a new endpoint thats return file from Weni Bucket
- Feature: Add is_active filter to User-Permission endpoint

## [2.0.0] - 2022-12-23
- Feature: Create endpoint for channel type

## [1.0.34] - 2022-11-18
- Feat: Create endpoint that returns success orgs

## [1.0.33] - 2022-11-17
- Fix:  Remove pagination_class from internal views
- Feat: Add internal Flow endpoint
- Feat: Add internal Classifier endpoint
- Feat: Add internal Org endpoint
- Feat: Add internal Channels endpoint
- Feat: Add internal Statistic endpoint
- Feat: Add internal User and User-Permission endpoint

## [1.0.32] - 2022-11-17
- Feat: Use internal_tickter false on TemplateOrg creation

## [1.0.31] - 2022-11-08
- Fix: fix org is_suspend endpoint

## [1.0.30] - 2022-11-07
- Feat: A endpoint to add a warning message to user showing org will be suspeded.
- Feat: A endpoint to suspend a org

## [1.0.29] - 2022-10-20
- Fix: Set Channel Stats start date to 01/01/2000

## [1.0.28] - 2022-10-07
- Update weni-protobuffers to 1.2.18

## [1.0.27] - 2022-10-07
- Add ticketer queues endpoint
- Add agent permission in UserPermission retrieve endpoint
- Add endpoint that allows managing ticketer queues
- Endpoint that allows you to create, update and destroy a ticketer

## [1.0.26] - 2022-09-15
- Create serializer fields for User and Org using SlugRelatedField
- Org and User APIToken internal endpoint

## [1.0.25] - 2022-08-31
- Add org and is_active to channel list

## [1.0.24] - 2022-08-29
- Generate WAC channel name from number and verified_name

## [1.0.23] - 2022-08-26
- Endpoint that lets you create a flow from a sample flow
- Endpoint that allows you to create org from a template
- Create base classes for internal endpoints

## [1.0.22] - 2022-06-15
- Fix pipy package dependencies

## [1.0.21] - 2022-06-15
- Add channel_id field to response in billing Detailed endpoint
- Adjust the python version to have compatibility with the new package;
- Add a new package named pre-commit;
- Creates a file named .pre-commit-config.yaml to configure the pre commit;
- Adjust readme with the new feature.

## [1.0.20] - 2022-06-15
- Fix exception when has not msg on message detail

## [1.0.19] - 2022-06-09
- Add more details to Message endpoint

## [1.0.18] - 2022-06-08
- Add Channel Cloud Whatsapp

## [1.0.17] - 2022-05-02
- Added permission_type of users to org object

## [1.0.16] - 2022-04-19
### Revert
- "Refactors the billing query"

## [1.0.15] - 2022-04-18
### update
- weni-protobuffers version to 1.2.12

## [1.0.14] - 2022-04-05
### update
- weni-protobuffers version to 1.2.10

## [1.0.13] - 2022-02-25
### Feature
- Add the infinity plan when updating an org

## [1.0.12] - 2022-02-21
### Fixed
- Lock weni-protobuffers version to 1.2.7
- Reverts unnecessary billing commits

## [1.0.11] - 2022-02-18
### Fixed
- Redirect to /msg/inbox/ if authenticate without next param

## [1.0.10] - 2022-02-14
### Fixed
- Checks if the user is already authenticated to avoid unnecessary authentication

## [1.0.9] - 2022-01-20
### Fixed
- Refactors the billing query
- Refactor some billing endpoint nomenclatures and validate organization

## [1.0.8] - 2021-12-21
### Fixed
- Adjust BillingService return and exceptions

## [1.0.7] - 2021-12-03
### Fixed
- Adjust exceptions of channel service

## [1.0.6] - 2021-12-01
### Added
- Retrieve and List endpoints to Channel service
- Return HttpResponseBadRequest on invalid request data
- New fields to channel generic endpoint

## [1.0.5] - 2021-11-12
### Added
- Generic endpoint to create channels by ChannelType code

## [1.0.4] - 2021-11-04
### Fixed
- Removed sync=False on create classifier

## [1.0.3] - 2021-10-28
### Changed
- `weni-protobuffers` updated to 1.2.1

### Added
- Channel release endpoint (#76)

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
