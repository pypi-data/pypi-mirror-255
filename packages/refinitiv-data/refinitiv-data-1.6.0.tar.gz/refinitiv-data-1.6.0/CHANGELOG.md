# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- towncrier release notes start -->

## [1.6.0] - 2024-02-07

### Added

- `app_name` parameter in session object and user config to define Application Client ID Header. ([eapi-6117](https://jira.refinitiv.com/browse/eapi-6117))
- Proxies for asynchronous requests usage. ([eapi-6279](https://jira.refinitiv.com/browse/eapi-6279))

### Changed

- Dependency package versions is changed to: "appdirs~=1.4.4", "pyee>=9.0.4,<=11.1.0", "httpx>=0.18.0,<0.27.0", "httpcore<1.1.0", "numpy~=1.11", "pandas>=1.3.5,<3.0.0", "python-dateutil<3.0.0", "requests~=2.28", "scipy<1.13.0", "tenacity~=8.0", "watchdog>=0.10.2,<3.0.0", "websocket-client~=1.5,!=1.5.0,!=1.5.2", "pyhumps>=3.0.2,<4.0.0", "jinja2>=3.0.3,<4.0.0", "simplejson~=3.15". ([eapi-6069](https://jira.refinitiv.com/browse/eapi-6069))

### Removed

- `create`, `create_udc` and `create_basket` methods for Custom Instrument. ([dme-5394](https://jira.refinitiv.com/browse/dme-5394))

### Fixed

- Partially converted string values with dates to datetime64 dtype. ([eapi-6155](https://jira.refinitiv.com/browse/eapi-6155))
- Custom Instrument symbol name is splitted by symbols after adding to streaming. ([eapi-6198](https://jira.refinitiv.com/browse/eapi-6198))
- Authentication "quota is reached" error is thrown in session thread. ([eapi-6211](https://jira.refinitiv.com/browse/eapi-6211))
- Data argument is empty in refresh callback after Custom Instrument stream was reopened. ([eapi-6213](https://jira.refinitiv.com/browse/eapi-6213))
- unhashable type: 'list' - TypeError is raised for Discovery.Search request. ([eapi-6278](https://jira.refinitiv.com/browse/eapi-6278))


## [1.5.1] - 2023-12-14

### Changed

- Dataframe builder for `rd.content.custom_instruments.search`. ([eapi-6108](https://jira.refinitiv.com/browse/eapi-6108))
- Regex pattern is changed to get valid uuid using library hook with `rd.content.custom_instruments`. ([eapi-6149](https://jira.refinitiv.com/browse/eapi-6149))

### Fixed

- RSSL stream does not recover after network reconnection. ([eapi-6076](https://jira.refinitiv.com/browse/eapi-6076))
- Stream open message is sent if no fields record changed to update (add or remove). ([eapi-6020](https://jira.refinitiv.com/browse/eapi-6020))
- Apply initial `with_updates` argument value for stream.open() method when adding instrument or field to already opened pricing stream. ([eapi-6077](https://jira.refinitiv.com/browse/eapi-6077))


## [1.5.0] - 2023-11-06

### Added

- Warning message and logging in `debug` level, when get AlreadyOpen status for streaming with existed RIC in WS Connection. ([eapi-5238](https://jira.refinitiv.com/browse/eapi-5238))
- Ability to request amount over the limit of 200 items in `filing.search Definition`. ([eapi-5258](https://jira.refinitiv.com/browse/eapi-5258))
- `Ping` token management to support /auth/oauth2/v2 endpoint. ([eapi-5399](https://jira.refinitiv.com/browse/eapi-5399))
- Warning if the user defined adjustments parameter for custom_instrument universes or TR fields in `rd.get_history()`. ([eapi-5895](https://jira.refinitiv.com/browse/eapi-5895))
- Log full json response on error when refresh or renew the token. ([eapi-5986](https://jira.refinitiv.com/browse/eapi-5986))
- Warning for get_history, get_data when `parameters` parameter can not be applied. ([eapi-6007](https://jira.refinitiv.com/browse/eapi-6007))

### Changed

- httpcore package dependency max version to 17.2. ([eapi-5896](https://jira.refinitiv.com/browse/eapi-5896))
- Optimised `debug` log information. ([eapi-5700](https://jira.refinitiv.com/browse/eapi-5700))

### Fixed

- AttributeError raised in `refinitiv.data.eikon` if StreamingPrices opening with session parameter None. ([eapi-5897](https://jira.refinitiv.com/browse/eapi-5897))
- `rd.get_history` and `rd.content.custom_instrument.summaries` build multi-index dataframe with one field if custom instruments data was retrieved. ([eapi-5930](https://jira.refinitiv.com/browse/eapi-5930))
- Exception is raised if no data and headers returns to ADC response for SCREEN function with success status code. ([eapi-5967](https://jira.refinitiv.com/browse/eapi-5967))

### Performance adjustments

- Optimization of creation internal callbacks (avoid arguments sorting and anonymous function creation). ([eapi-5900](https://jira.refinitiv.com/browse/eapi-5900))
- Disable debug strings generation if `debug` log level is not set. ([eapi-5929](https://jira.refinitiv.com/browse/eapi-5929))
- Library import optimisation (avoid importing all library components at once. The load is distributed on Session, Content, Delivery, Access layer). ([eapi-5722](https://jira.refinitiv.com/browse/eapi-5722))


## [1.4.0] - 2023-09-07

### Added

- `ipa.financial_contracts.option` is splitted into `ipa.financial_contracts.fx_option` and `ipa.financial_contracts.eti_option`. ([eapi-5492](https://jira.refinitiv.com/browse/eapi-5492))
- `api` parameter to `rd.content.pricing.chain.Definition()`. ([eapi-5553](https://jira.refinitiv.com/browse/eapi-5553))
- `Access` and `Refresh` token revoke mechanism. ([eapi-5565](https://jira.refinitiv.com/browse/eapi-5565))
- Strip leading/trailing spaces in url from config params specified in json files. ([eapi-5648](https://jira.refinitiv.com/browse/eapi-5648))
- Dispatching WS login events results. `StreamAuthenticationFailed` and `StreamAuthenticationSuccess` session events. ([eapi-5788](https://jira.refinitiv.com/browse/eapi-5788))

### Changed

- Minimum value for `news.headlins` count parameter to 0. ([eapi-5214](https://jira.refinitiv.com/browse/eapi-5214))
- `rd.open_session` opens one default session in runtime. ([eapi-5632](https://jira.refinitiv.com/browse/eapi-5632))
- `pandas` package dependency max version to 2.0.2. ([eapi-5650](https://jira.refinitiv.com/browse/eapi-5650))
- `httpx` package dependency max version to 0.24.1. ([eapi-5694](https://jira.refinitiv.com/browse/eapi-5694))

### Fixed

- Incorrect encoding for delayed RIC in streaming request when retrieving data with `rd.get_data()` ([eapi-5789](https://jira.refinitiv.com/browse/eapi-5789))
- ADC formula's field with "date" parameter returns datetime64[ns] dtype instead of int with `rd.get_data()` ([eapi-5797](https://jira.refinitiv.com/browse/eapi-5797))
- Raised RDError when unexpected string values tried to be converted to date format for `rd.get_data()` ([eapi-5840](https://jira.refinitiv.com/browse/eapi-5840))

### Performance adjustments

- Working with listeners of streams is optimised. Decreased memory consumption. Added subscribe/unsubscribe methods. ([eapi-5458](https://jira.refinitiv.com/browse/eapi-5458), [eapi-5782](https://jira.refinitiv.com/browse/EAPI-5782))

### Deprecation

- `FutureWarning` message if User passed positional argument to `ipa.curves` Definition() or `ipa.surfaces` Definition(). Only named parameters will be allowed in a future version. ([eapi-5635](https://jira.refinitiv.com/browse/eapi-5635))
- `FutureWarning` message if `signon_control` parameter isn't defined in config file. It will have `False` value by default in future versions. ([eapi-5636](https://jira.refinitiv.com/browse/eapi-5636))
- Deprecated `refinitiv.data.eikon` module will be removed in a future 2.x version. ([eapi-5637](https://jira.refinitiv.com/browse/eapi-5637))
- Deprecated `refinitiv.data.content.trade_data_service` module will be removed in a future 2.x version. ([eapi-5638](https://jira.refinitiv.com/browse/eapi-5638))
- `SwaptionMarketDataRule` have been deprecated and will be removed in a future 2.x version. ([eapi-5639](https://jira.refinitiv.com/browse/eapi-5639))
- `FutureWarning` message if `instrument_type` class parameter defined in `rd.content.ipa.surfaces.cap.Definition`, `rd.content.ipa.surfaces.swaption.Definition`. Parameter will be removed in a future 2.x version. ([eapi-5640](https://jira.refinitiv.com/browse/eapi-5640)) 
- `FutureWarning` message if `income_tax_percent` class argument passed to `rd.content.ipa.financial_contracts.term_deposit.PricingParameters`. Parameter will be removed in a future 2.x version. ([eapi-5640](https://jira.refinitiv.com/browse/eapi-5640))
- `FutureWarning` message if User defined positional parameter in `ipa.financial_contract` Definition(). Only named parameters will be allowed in a future 2.x version. ([eapi-5641](https://jira.refinitiv.com/browse/eapi-5641))
- Deprecated `on_response` parameter in synchronous get_data() method will be removed in a future 2.x version. ([eapi-5642](https://jira.refinitiv.com/browse/eapi-5642))
- Response properties - http_status, http_response, request_message or http_headers will be moved inside Response.raw property in a future 2.x version. ([eapi-5655](https://jira.refinitiv.com/browse/eapi-5655))
- `udf underlying-platform` support is completely dropping off for news `headlines` and `stories` ([eapi-5379](https://jira.refinitiv.com/browse/eapi-5379))

### Hidden

- `refinitiv.data.content.ipa.curves._cross_currency_curves` moved to `refinitiv.data.early_access.content.ipa.curves.cross_currency_curves` ([eapi-5645](https://jira.refinitiv.com/browse/eapi-5645))
- customers.org_ids and suppliers.org_ids attributes for `refinitiv.data.discovery._stakeholders`. ([eapi-5666](https://jira.refinitiv.com/browse/eapi-5666))


## [1.3.1] - 2023-07-31

### Fixed

- RIC with upper case register letters passed to pricing endpoint in `rd.get_data` request, if mix of register letters were defined by User ([eapi-5733](https://jira.refinitiv.com/browse/eapi-5733))


## [1.3.0] - 2023-06-21

### Added

- `datetime` types for date measuring parameters to `refinitiv.data.content.ipa` objects ([eapi-5062](https://jira.refinitiv.com/browse/eapi-5062))
- Fields validation option to the `contribute()` method for updating instrument(RIC) ([eapi-5213](https://jira.refinitiv.com/browse/eapi-5213))
- `proxies` parameter to platform session ([eapi-5493](https://jira.refinitiv.com/browse/eapi-5493))

### Changed

- Updated docstrings for whole Delivery layer and the Content layer for the following parts: ESG, Estimates, Pricing, Symbol conversion ([eapi-5217](https://jira.refinitiv.com/browse/eapi-5217))
- Optimising the logic of custom-instruments requests by saving `uuid` in cache ([eapi-5357](https://jira.refinitiv.com/browse/eapi-5357))
- `Instrument` header name registered is unified for rdp/udf responses ([eapi-5387](https://jira.refinitiv.com/browse/eapi-5387))
- Unified logic for displaying headers in `rd.get_history` DataFrame ([eapi-5454](https://jira.refinitiv.com/browse/eapi-5454))
- `axis` parameter can be defined as `string` in `surface.get_point()` and `surface.get_curve()` methods ([eapi-5473](https://jira.refinitiv.com/browse/eapi-5473))

### Fixed

- `KeyError` raised if returns empty response in `cfs.packages` ([eapi-5634](https://jira.refinitiv.com/browse/eapi-5634))
- `TypeError` raised instead of meaningful error message from response in `ipa.forward_curves` ([eapi-5631](https://jira.refinitiv.com/browse/eapi-5631))
- `ValueError` raised if different case on duplicated fields defined in `rd.get_history` request ([eapi-5453](https://jira.refinitiv.com/browse/eapi-5453))
- `search_explorer.get_possible_values()` is raise KeyError if no Navigators key exists ([eapi-5542](https://jira.refinitiv.com/browse/eapi-5542))

### Hidden

- Additional columns are added to DataFrame for customers and suppliers, renamed `fetch()` to `get_data()` ([eapi-5382](https://jira.refinitiv.com/browse/eapi-5382))
- `Property.get_possible_values` method will not request data every call but check data in previous search response ([eapi-5490](https://jira.refinitiv.com/browse/eapi-5490))
- `metadata` property is removed from `SearchPropertyExploreResponse` ([eapi-5491](https://jira.refinitiv.com/browse/eapi-5491))


## [1.2.0] - 2023-05-02

### Added

- `extended_params` parameter to `Definition` classes of the following submodules of the `refinitiv.data.content.news` module: `online_reports`, `online_reports`, `top_news`, `top_news`, `story` ([eapi-4976](https://jira.refinitiv.com/browse/eapi-4976))
- `instrument_type` parameter to the `refinitiv.data.content.ipa.financial_contracts.bond.Definition` ([eapi-5001](https://jira.refinitiv.com/browse/eapi-5001))
- `refinitiv.data.content.ipa.surfaces.eti.VolatilitySurfacePoint` ([eapi-5020](https://jira.refinitiv.com/browse/eapi-5020))
- New parameters for the `refinitiv.data.content.filings.search.Definition` to simplify search: `form_type,` `feed,` `org_id,` `start_date,` `end_date,` `text,` `sections,` `limit,` `sort_order` ([eapi-5204](https://jira.refinitiv.com/browse/eapi-5204))
- `closure` parameter for `refinitiv.data.content.fundamental_and_reference.Definition().get_data_async()` ([eapi-5236](https://jira.refinitiv.com/browse/eapi-5236))

### Changed

- Upgraded `refinitiv.data.content.ipa.financial_contracts` endpoint to 1.0.180 ([eapi-4267](https://jira.refinitiv.com/browse/eapi-4267))
- Upgraded `refinitiv.data.content.ipa.curves_and_surfaces` endpoint to 1.0.130 ([eapi-4268](https://jira.refinitiv.com/browse/eapi-4268))
- WebSocket streams support Decimals input, rendering them with trailing zeroes ([eapi-4836](https://jira.refinitiv.com/browse/eapi-4836))
- Caching subtemplates results during one search template call ([eapi-4838](https://jira.refinitiv.com/browse/eapi-4838))
- String Enums can be used as strings, string Enum arguments accept strings too ([eapi-4846](https://jira.refinitiv.com/browse/eapi-4846))
- Updated error management for `refinitiv.data.get_data()` ([eapi-5022](https://jira.refinitiv.com/browse/eapi-5022))
  - `get_data()` sends requests to ADC and pricing. If one of the API returns data, `get_data()` displays them. If two APIs return the errors - `get_data()` concatenates error messages and raises `RDerror`
- Off-stream pricing contribution uses pricing section by default, old custom config section is still supported ([eapi-5076](https://jira.refinitiv.com/browse/eapi-5076))
- `IPA swaption`: show warning when creation of dataframe and surface object from the the raw data is not supported ([eapi-5148](https://jira.refinitiv.com/browse/eapi-5148))

### Fixed

- `ScopeError` was raised in some situation when use actually has access to the endpoint ([eapi-4861](https://jira.refinitiv.com/browse/eapi-4861))
- On-stream contrib at content level always returns "Can't contribute to unsubscribed item" error ([eapi-4864](https://jira.refinitiv.com/browse/eapi-4864))
- Warning message from pandas 1.5.0 ([eapi-4987](https://jira.refinitiv.com/browse/eapi-4987))
- Empty result of sub-templates raised exception in search templates. Now, if required sub-templates don't have required data we return an empty DataFrame as a result of a root search template call. ([eapi-4990](https://jira.refinitiv.com/browse/eapi-4990))
- `ValueError` raised on dataframe access of `BondFuture` result with `DeliveryBasket` field ([eapi-5027](https://jira.refinitiv.com/browse/eapi-5027))
- One pricing stream was used if you have two endpoints, and launch them both in parallel ([eapi-5080](https://jira.refinitiv.com/browse/eapi-5080))
- Exception "TypeError: tuple expected at most 1 argument, got 2" when using a proxy configuration with username and password ([eapi-5185](https://jira.refinitiv.com/browse/eapi-5185))
- `refinitiv.data.content.news`: exceptions when working with specific versions of Refinitiv Workspace ([eapi-5206](https://jira.refinitiv.com/browse/eapi-5206))
- `ADC` field functions are case insensitive ([eapi-5209](https://jira.refinitiv.com/browse/eapi-5209))
- Some date columns returned by `refinitiv.data.get_data` had string data type ([eapi-5220](https://jira.refinitiv.com/browse/eapi-5220))
- `start` and `end` parameters value is calculated slightly different values by timedelta in the time of any next request was created ([eapi-5225](https://jira.refinitiv.com/browse/eapi-5225))
- `refinitiv.data.get_history()` sends duplicated requests to pricing endpoint based on amount of RICs in ADC response. ([eapi-5226](https://jira.refinitiv.com/browse/eapi-5226), [eapi-5395](https://jira.refinitiv.com/browse/eapi-5395))
- `ADC` formula's field with "date" parameter returns datetime64[ns] dtype instead of int with get_data() ([eapi-5261](https://jira.refinitiv.com/browse/eapi-5261))
- `refinitiv.data.news.get_story()` returned `None` with desktop session on the rdp platform ([eapi-5262](https://jira.refinitiv.com/browse/eapi-5262))
- Misformed `Position` value in OMM streaming login message ([eapi-5302](https://jira.refinitiv.com/browse/eapi-5302))
- `ValueError` exception when trying to close a pricing stream with a big number of rics ([eapi-5303](https://jira.refinitiv.com/browse/eapi-5303))
- `closure` parameter was ignored in `get_async_method` of `headlines.Definition` and `story.Definition` objects of `refinitiv.data.content.news` module ([eapi-5329](https://jira.refinitiv.com/browse/eapi-5329))

### Hidden

- Internal classes for retrieving field dictionaries and validating values for OMM stream contributions ([eapi-4662](https://jira.refinitiv.com/browse/eapi-4662), [eapi-5046](https://jira.refinitiv.com/browse/eapi-5046))
- Expose `Customers` and `Suppliers` objects as a part of the `refinitiv.data.early_access.discovery` module ([eapi-4931](https://jira.refinitiv.com/browse/eapi-4931), [eapi-5347](https://jira.refinitiv.com/browse/eapi-5347))
- `refinitiv.data._qpl.fx_swp_to_swp` optional arguments made keyword only ([eapi-4994](https://jira.refinitiv.com/browse/eapi-4994))
- `SearchExplorer()` is added to the early access module - basic implementation ([eapi-5090](https://jira.refinitiv.com/browse/eapi-5090))


## [1.1.1] - 2023-02-23

### Fixed

- `refinitiv.data.get_data`
    - ADC functions with underscores in their name were not recognized as ADC functions. Requests for ADC was not made ([eapi-5070](https://jira.refinitiv.com/browse/eapi-5070))
    - Non-date TR fields with "date" in their name were wrongly converted to date type ([eapi-5154](https://jira.refinitiv.com/browse/eapi-5154))
- IPA surfaces
    - IPA surface object initialization error when NDimensionalArray was requested ([eapi-3135](https://jira.refinitiv.com/browse/eapi-3135))
    - IPA surfaces results raised AttributeError on dataframe access when surface_parameters parameter is not defined ([eapi-5089](https://jira.refinitiv.com/browse/eapi-5089))
    - IPA surfaces results raised exceptions on non-numeric data points values when accessing their dataframe ([eapi-5078](https://jira.refinitiv.com/browse/eapi-5078))
- AttributeError was raised when calling `StreamConnection.dispose()` method on high load ([eapi-5077](https://jira.refinitiv.com/browse/eapi-5077))
- Exceptions sometimes thrown when contributing on macOS ([eapi-5082](https://jira.refinitiv.com/browse/eapi-5082))
- Slow download speed on CFS / ESG Bulk ([eapi-5127](https://jira.refinitiv.com/browse/eapi-5127))


## [1.1.0] - 2023-02-01

### Added

- `refinitiv.data.discovery.convert_symbols` function ([eapi-4897](https://jira.refinitiv.com/browse/eapi-4897))

### Changed

- `width`, `height`, `extended_params` parameters added for `refinitiv.data.content.news.images.Definition`
- `parameters` parameter for `refinitiv.data.get_history` ([eapi-4920](https://jira.refinitiv.com/browse/eapi-4920))
  - As for `refinitiv.data.get_data()`, the `parameters` parameter overrides request parameters sent to DataGrid/ADC.

### Fixed

- Dataframe field data is converted to date format instead of int for AVG function in `rd.get_data()`, `fundamental_and_reference` and others ([eapi-4988](https://jira.refinitiv.com/browse/eapi-4988))
- Optimize number of requests to ADC on access layer functions in certain situations - `refinitiv.data.discovery.Chain()` returns partial constituents on certain sets of user permissions ([eapi-4951](https://jira.refinitiv.com/browse/eapi-4951))
- Invalid characters on save for some images from `refinitiv.data.content.news` ([eapi-4930](https://jira.refinitiv.com/browse/eapi-4930))
- Zero values was converted to `<NA>` on pricing stream snapshot - pricing stream has a state `OpenState.Pending` after `ScopeError` exception was raised ([eapi-4986](https://jira.refinitiv.com/browse/eapi-4986))


## [1.0.0] - 2022-12-26

First public release. Changes from the latest beta version (1.0.0b28post0).

### Added

- `refinitiv.data.content.news.images` and  `refinitiv.data.content.news.top_news` objects ([eapi-4771](https://jira.refinitiv.com/browse/eapi-4771), [eapi-4768](https://jira.refinitiv.com/browse/eapi-4768))

### Fixed

- Raising incorrect error when user does not have required permission scope for `refinitiv.data.discovery.Chain` ([eapi-4766](https://jira.refinitiv.com/browse/eapi-4766))
- Incorrect management of RICs with special characters by `refinitiv.data.get_data`
