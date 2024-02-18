# Changelog for the Python SDK for the semantha platform

## [6.8.0] 2024-02-09
### Removed
- Removed two setting values: similarity_matcher and similarity_threshold for endpoint: **/domains/{domainname}/settings** **GET**

### Improved
- More method and parameter comments
- Endpoint **/domains** **GET** returns DomainInfo object now instead of Domain

## [6.7.0] 2024-01-29
### Improved
- More class and method comments, improved styling

## [6.6.0] 2024-01-18
### Added
- Added transactions endpoint: **/domains/{domainname}/transactions** **GET**

### Removed
- Removed deprecated endpoint: **/domains/{domainname}/documentcomparisons**

## [6.5.0] 2023-12-21
### Improved

- Reuse session object of requests library to increase performance on multiple calls

## [6.4.0] 2023-12-07
### Removed
- **/model/domains/{domainname}/documentcomparisons** **POST** (Accept: xlsx)

## [6.3.0] 2023-11-21
### Fixed
- PATCH and PUT methods with a list of dataclasses wasn't working.

### Added
- Added language parameter to /answers and /summarizations endpoints.

## [6.2.1] 2023-11-13
### Fixed
- Dataclasses aren't frozen anymore.
- Improved permission denied message with url.

## [6.2.0] 2023-11-09
### Added
- server_url is read from credentials.properties file now -> semantha_sdk.login(key_file = "credentials.properties") parameter key_file is enough now.
- server_url is read from json config file if present.
- Checks to normalize server_url

## [6.1.0] 2023-10-25
This version should only be used with a semantha server version >= 6.1

### Changed
- /api/info is versioned now and SDK calls /api/v3/info internally. This is a breaking change
- login() function and SemanthaAPI class are generated now

## [6.0.1] 2023-10-17
### Added
- Support for OAuth 2.0 Client Credentials Flow for credentials created via Semantha Administration UI.

## [6.0.0] 2023-10-04
### Fixed
- GET of files with different mimetype than application/json (e.g. get_as_docx)

## [5.11.1] 2023-09-21
### Removed
- **/model/domains/{domainname}/extractortables** has been removed
- **/model/domains/{domainname}/extractortables/{id}** has been removed

### Fixed
- fixed serialization on post of bulk endpoints with list of objects

## [5.11.0]
### Changed
- **/api/domains/{domainname}/summarizations** returns an object now instead of string.
- renamed class Metadata to ModelMetadata

## [5.10.0]
Improved Use Case SDK

## [5.9.0]
### Removed
- **/api/domains/{domainname}/referencedocuments/{documentid}/paragraphs/{id}/links**

## [5.8.0]
### Added
- **/api/domains/{domainname}/documentclasses/{id}/documentclasses**
- **/api/domains/{domainname}/documentclasses/{id}/referencedocuments**
- **/api/domains/{domainname}/referencedocuments/{documentid}/paragraphs/{id}/links**
- **/api/model/domains/{domainname}/backups**

SDK covers now 193/197 services.

## [5.7.0]
Added new endpoints in:
- **/api/domains/{domainname}/documenttypes/*** 
- **/api/domains/{domainname}/documentclasses/{id}/customfields**
- **/api/model/domains/{domainname}/classes/***

SDK covers now 184/197 services.


## [5.6.0]
Added most endpoints in **/api/models/* **
SDK covers now 158/180 services.

## [5.5.0]
Removed language parameter on **/api/domains/{domainname}/references**
Fixed bug on serialization of **/api/domains/{domainname}/modelinstances** response.
Fixed return of binary responses of bulk services.

## [5.4.0]
Added **new** service: 
- **/api/domains/{domainname}/summarizations** which generations a summarization for a given list of texts and a given topic.

Added support for **existing** services: 
- /api/model/domains/{domainname}/boostwords/{id}
- /api/model/domains/{domainname}/namedentities
- /api/model/domains/{domainname}/namedentities/{id}
- /api/model/domains/{domainname}/stopwords
- /api/model/domains/{domainname}/stopwords/{id}
- /api/model/domains/{domainname}/synonyms/{id}

## [5.3.0]

Added new service: **/api/domains/{domainid}/answers** with retrieval augemented answer generation based on your library entries.
Added new parameter on /modelinstances

## [5.2.0]

The SDK is now automatically generated from our openapi.json specification. It covers 71/169 (=42%) of all available services. Many class names and package names have been changed.

## [4.5.0]
Major restructuring of the SDK.
All sub-resources are directly accessible (instead of invoking getters).
That also means that (except for a few) all functions are plain get/post/delete/put/patch.
For example, in Versions < 4.5.0 a domain resource was fetched using `semantha_sdk.domains.get_one("domain_name")`.
Starting with 4.5.0 it is `semantha_sdk.domains("domain_name")`.
That also means that get/post/put/patch functions return semantha model objects (and never resources), which makes usage more consistent.
