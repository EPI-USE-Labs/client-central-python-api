## v12.5.8 (2024-11-19)

### Fix

- **Dependancy**: Update aiohttp to 3.11.4

## v12.5.7 (2024-02-29)

### Fix

- **dependancies**: Updates aiohttp, ujson and beautifulsoup

## v12.5.6 (2023-11-20)

### Fix

- **Query**: Fix query tickets not parsing along Async status

## v12.5.5 (2023-11-20)

### Fix

- **Users**: Fix async get_user_by_email

## v12.5.4 (2023-11-20)

### Fix

- **Roles**: Fix async roles

## v12.5.3 (2023-11-20)

### Fix

- **Roles**: Fix async for roles

## v12.5.2 (2023-11-20)

### Fix

- **Ticket**: Fix query async

## v12.5.1 (2023-11-20)

### Fix

- **Ticket**: Fix async session creation for Tickets

## v12.5.0 (2023-11-20)

### Feat

- **Ticket**: Added attachment API

## v12.4.2 (2023-11-16)

### Fix

- **CI**: Bump release

## v12.4.1 (2023-11-16)

### Fix

- **Ticket**: Added status to ticket creation. Added payload for debugging when an exception is raised

## v12.4.0 (2023-04-21)

### Feat

- **users**: Lock and unlock user functionality

## v12.3.1 (2023-04-20)

### Fix

- **ticket**: Allow customer_vp/owner to be None

## v12.3.0 (2023-02-24)

### Feat

- **ticket**: added add_user_watcher_by_email

## v12.2.2 (2023-02-09)

### Fix

- **ticket**: Fix not commiting customer_vp, fix assignee being overwritten

## v12.2.1 (2023-02-08)

### Fix

- **bump**: bump

## v12.1.0 (2023-02-08)

### Feat

- **added customer_user_vp parameter**: added customer_user_vp to Ticket
- Update user model to include

## v12.0.1 (2022-02-01)

### Fix

- **bump**: bump version to create new release

## v12.0.0 (2022-02-01)

### BREAKING CHANGE

- Deprecations in Python 3.10 have been fixed as well, this however pushed the
minimum Python version to 3.7

### Fix

- **ticket**: fix default parameter values and static variables

## v11.1.2 (2021-10-20)

### Fix

- **__init__**: fix version incorrectly captured

## v11.1.1 (2021-10-20)

### Fix

- **__init__**: fix version incorrectly captured

## v11.1.0 (2021-10-20)

### Feat

- **ticket**: added flag to allow toggling of sending notifications on updates to a ticket

## v11.0.4 (2021-08-05)

### Fix

- **ticket**: remove debugging output

## v11.0.3 (2021-08-05)

### Fix

- **dependancies**: remove typing as it has been included in the stdlib

## v11.0.2 (2021-08-05)

### Fix

- **setup.py**: manually bump version

## v11.0.1 (2021-08-05)

### Fix

- **setup.py**: update required python version. Fix quotes

## v11.0.0 (2021-08-05)

### BREAKING CHANGE

- Upstream  date format changed, Upstream roles endpoint changed.

### Feat

- **dependancies**: update dependancies to latest stable version

### Fix

- **ticket**: updated library to support non microsecond time format, Updated roles to match upstream

## v10.0.4 (2021-02-01)

### Fix

- fix bump version setup

## v10.0.3 (2021-02-01)

### Fix

- bump release

## v10.0.2 (2021-02-01)

### Fix

- **Ticket**: Added missing payload data for related tickets

## v10.0.1 (2020-07-30)

### Fix

- **Testing**: Updated tests to reflect CC changes for both tokens and auto spacing for ticket format

## v10.0.0 (2020-06-04)

### BREAKING CHANGE

- visible_to_customer has been replaced with internal

### Fix

- **Ticket by ID and tickets by query**: Fix bug where if the ticket was created from an email route
- **ticket**: Updated to match CC API. visible_to_customer has been replaced with internal.

## v9.2.2 (2020-04-15)

### Fix

- **CC**: Removed regex check for token since it is not valid.

## v9.2.1 (2020-04-15)

### Fix

- **Ticket queries.**: Check if account is not null.

## v9.2.0 (2020-03-27)

### Feat

- **ClientCentral**: More verification if tokens are correct and present

## v9.1.2 (2020-03-27)

### Fix

- **Requests**: Added URL and method to requests in Ticket.

## v9.1.1 (2020-03-27)

### Fix

- **Exceptions**: Fixed HTTP Error when certain keys are missing in the payload.

## v9.1.0 (2020-03-03)

### Feat

- **Dependencies**: Updated all dependencies to latest version.

## v9.0.0 (2020-03-03)

### BREAKING CHANGE

- User Manager renamed to Users Client

### Feat

- **Users Client**: Added the function get_user_by_email

## v8.2.0 (2019-10-14)

### Feat

- **Ticket**: Get description text now replaces <br> with newlines.

## v8.1.9 (2019-09-27)

### Fix

- **Gitlab CI**: Version fix attempts.

## v8.1.8 (2019-09-27)

### Fix

- **Gitlab CI**: Change npm execution

## v8.1.7 (2019-09-27)

### Fix

- **Gitlab CI**: More attempts to fix publish step.

## v8.1.6 (2019-09-27)

### Fix

- **Gitlab CI**: Update the base image.

## v8.1.5 (2019-09-27)

### Fix

- **Gitlab CI**: Change imags in attempt to get setuptools working

## v8.1.4 (2019-09-27)

### Fix

- **Ticket**: Testing improvements

## v8.1.3 (2019-09-27)

### Fix

- **Query**: Fix ticket query objects not containing all the required fields.

## v8.1.2 (2019-09-26)

### Fix

- **ClientCentral**: Update all requirements.

## v8.1.1 (2019-09-26)

### Fix

- **Gitlab CI**: Attempted fix for twine upload.

## v8.1.0 (2019-09-26)

### Feat

- **Ticket**: Added the ability to make the commit event visible to customer.

## v8.0.2 (2019-09-16)

### Fix

- **CI**: Added missing publish file.

## v8.0.1 (2019-09-13)

### Fix

- **Client central**: Better sessions management.

## v8.0.0 (2019-09-11)

### BREAKING CHANGE

- Requests are no longer used. Everyting is built on the aiohttp library.

### Feat

- **End to end tests for both async and sync implementations.**: 
- **Ticket**: Converted main ticket methods to aiohttp. Created benchmarks to compare.

## v7.7.1 (2019-08-26)

### Fix

- **ClientCentral**: Fix passing a token via the constructor gets overridden by the conig file.

## v7.7.0 (2019-08-12)

### Feat

- **Requirements**: Updated stable requirments

## v7.6.3 (2019-08-12)

### Fix

- **Ticket status.**: Workaround for a change or bug in ClientCentral.

## v7.6.2 (2019-07-15)

### Fix

- **Tickets**: Fix if customer user is Null

## v7.6.1 (2019-07-15)

### Fix

- **Ticket**: Fix crash when customer does not exist.

## v7.6.0 (2019-07-09)

### Feat

- **Status**: Added the property "closed".

## v7.5.0 (2019-07-08)

### Feat

- **Tickets**: Added ability to get the human URL for the ticket.
- **Tickets**: Added ability to get the human URL for the ticket.

## v7.4.0 (2019-07-08)

### Feat

- **Status**: Status now includes a field called open which is a boolean value

## v7.3.0 (2019-07-08)

### Feat

- **ClienCentral**: Reuse Roles and Users managers for efficiency.

## v7.2.0 (2019-07-05)

### Feat

- **ClientCentral**: Added function to get role by name.

## v7.1.1 (2019-07-04)

### Fix

- **UsersManager**: Forgot to commit new sub module.

## v7.1.0 (2019-07-04)

### Feat

- **UsersManager**: Started implementing users implementation. Currently only get_user_by_id is func

## v7.0.0 (2019-07-04)

### BREAKING CHANGE

- Priority is now always required when creating a new ticket.

### Fix

- **ticket**: Default parameters in wrong order.
- **Ticket**: Force specifying priorty as it can change between accounts.

## v6.0.2 (2019-07-02)

### Fix

- **Ticket.comment**: Explicitly set the visible_to_customer field.

## v6.0.1 (2019-07-01)

### Fix

- **Ticket**: Potential fix for #9

## v6.0.0 (2019-07-01)

### BREAKING CHANGE

- Missing files are now added.

### Fix

- **ClientCentral**: Added missing files.

## v5.7.0 (2019-07-01)

### Feat

- **ClientCentral**: Added get roles functionality.

## v5.6.0 (2019-06-20)

### Feat

- **ticket**: Added flag to allow not updating the ticket when adding a user for the case where you

## v5.5.0 (2019-06-20)

### Feat

- **tickets and comments**: Added get_text_description which will remove the 'html' tags from the te

## v5.4.2 (2019-06-12)

### Fix

- **tickets**: available buttons are now properly lazy loaded.

### Refactor

- **tickets**: Unused code.

## v5.4.1 (2019-06-10)

### Fix

- **tickets**: assignee require the "User:" or "Role:" prefix.

## v5.4.0 (2019-06-10)

### Feat

- **tickets**: Related tickets are now lazy loaded along with other ticket specific options.

## v5.3.0 (2019-06-07)

### Feat

- **tickets**: Related tickets get request has been implmented in CC.

## v5.2.1 (2019-06-06)

### Fix

- **ticket**: Add watcher by user_id fixed.

## v5.2.0 (2019-06-06)

### Feat

- **tickets**: Added ability to add related tickets on creation of ticket.

## v5.1.2 (2019-06-05)

### Fix

- **ticket commenting**: Ability to comment on tickets even if the 'comment' button is not available.

## v5.1.1 (2019-06-05)

### Fix

- **tickets, query**: Fixed titles that are now possible in production would crash if None.

### Refactor

- **formatting**: Switched to black autoforamtting for py38. Removed isort.
- **all**: Switched to black formatter.

## v5.1.0 (2019-05-27)

### Feat

- **ticket**: Ability to bump ticket prio.

## v5.0.0 (2019-05-27)

### BREAKING CHANGE

- Removed old button functions.

### Feat

- **ticket button**: Buttons can now be pressed via the name of the button

## v4.1.0 (2019-05-17)

### Feat

- **ticket**: Custom fields are now saved in a dictionary.

## v4.0.0 (2019-05-17)

### BREAKING CHANGE

- User.name does not exist anymore, should now use user.first_name and user.last_name

### Feat

- **ticket**: User object now has job_title and title. Ticket events now have the visible_to_custome

## v3.0.3 (2019-05-09)

### Fix

- **bandit**: Ignore bandit hardcoded passwords.
- **ticket**: Tickets now have a property for both the creator and the owner of a ticket.

## v3.0.2 (2019-05-03)

### Fix

- **events**: Fixed duplicate events. Added tests to confirm this does not regress in the future.

### Refactor

- **query object**: Fixed type hints.

## v3.0.1 (2019-05-03)

### Fix

- **config**: Config file paths should now be OS independant.
- **all**: mypy type enforcement applied to general files.

## v3.0.0 (2019-05-02)

### BREAKING CHANGE

- Moved model to be a submodule of clientcentral.

### Fix

- **model**: Query required the full path to class.
- **pip**: Install config files.
- **model**: Fixed migration.

### Refactor

- **model**: Moved model to be a submodule of clientcentral.

## v2.0.0 (2019-04-29)

### BREAKING CHANGE

- Change of how events operate.
- Chagned ticket TypeObject

### Feat

- **tickets**: Added lazy loading for events, comments and change_events.
- **query**: Queried tickets are loaded in from query
- **tickets**: Added custom Exceptions. Added Object oriented type.

### Refactor

- **all**: Auto-formatting to pep8 conventions.

## v1.1.0 (2019-04-24)

### Feat

- **ticket**: Custom fields are now modifiable, however due to API limitations the custom field can
- **ticket**: Workspace and Project can now be set. The default project Id is 8.
- **ticket**: Events are now Object Oriented, Comment is a type of TicketEvent.
- **tickets**: Add ability to create simple queries.
- **tickets**: Added Object Oriented comments attribute.
- **ticket**: Ticket now has an Object Oriented status.
- **ticket**: Users are now object oriented including email, name as well as user_id

### Refactor

- **ticket**: Comments are now events. This models ClientCentral's models more accurately.
- **All**: Auto-format pep8.

## v1.0.0 (2019-04-17)

### Feat

- **All**: Initial commit to fresh repository.
