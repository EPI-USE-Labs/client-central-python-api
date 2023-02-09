# clientcentral-api-python
[![version](https://img.shields.io/badge/version-12.2.2-brightgreen.svg)]()
[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)

# Install
```bash
pip install clientcentral --user
```
# Upgrading
```bash
pip install --user --upgrade clientcentral
```

A specific version can also be installed by adding the tag:
```bash
pip install --user --upgrade clientcentral==12.2.2
```

# Requirements
This library was built and tested on `Python 3.11` a minimal Python version of `Python 3.7.x` is required.

`Python 2` is not supported.

# Features
- Object Oriented API
- Querying
- Lazy loading (Events)

# Config
The token that will be used can either be sent as an environement variable:
```bash
CC_TOKEN=<TOKEN> python3 main.py
```
or parsed to the constructor:
```python
cc = ClientCentral(production=True, token="123")
```

# Example usage

```python
import clientcentral.ticketformatting as tf
from clientcentral.clientcentral import ClientCentral

# Production 'false' will run on qa.cc
cc = ClientCentral(production=True)

# This will create a ticket in the Managed Services workspace.
# In this example custom_fields {"id": 17, "values": 0} refer to "Security related" -> "No"
# Theses values can be found by following the following instructions: https://clientcentral.io/support/cc/kb/articles/1661-tickets-api-creating-tickets
ticket = cc.create_ticket(subject="New awesome subject" ,
                          description="this is an awesome ticket",
                          account_vp=1,
                          customer_user_vp=1,
                          project_id=8,
                          workspace_id=16,
                          custom_fields_attributes=[{
                              "id": 17,
                              "values": 0
                          }, {
                              "id": 75,
                              "values": 363
                          }])

ticket.comment("<p>" + tf.bold("I am BOLD") + "</p>")

# Get the ticket's creator
print("Ticket creator: " + ticket.owner.name)

# Get the ticket's status
print("Ticket status:" + ticket.status.name)

# Print the ticket's description
print("Ticket description: " + ticket.description)

# Add a user to watchers
ticket.add_user_watcher(14012) # 14012 refers to the user id in this case its "Thomas Scholtz"

# Change the description of the ticket
ticket.description = "New and improved ticket description"

# Finally after making all changes commit them.
ticket.commit()

for comment in ticket.comments:
    if comment.created_by_user:
        print("Comment from: " + comment.created_by_user.name + " says: " + comment.comment)

# Ticket events, change_events and comments are lazy loaded.
for change_event in ticket.change_events:
    if change_event.created_by_user:
        print("Change by: " + str(change_event.created_by_user.name))
    for change in change_event.changes:
        print("Changed: " + str(change.name) + " from: " + str(change.from_value) + " to: " + str(change.to_value))
```

# Example query
```python
from clientcentral.clientcentral import ClientCentral
import clientcentral.query as operators

# Production 'false' will run on qa.clientcentral.io
cc = ClientCentral(production=True)

# This will return a list of all tickets that are:
# open,
# in workspace with id 87,
# created by the user with the email 'thomas@labs.epiuse.com',
# has not been updated since 2019-02-20,
# subject contains 'New awesome subject'
tickets = cc.query_tickets().filter_by(
            operators.and_( operators.statement("status.open"),
                            operators.comparison("workspace_id", "=", "87"),
                            operators.comparison("created_by_user.email", "=", "'thomas@labs.epiuse.com'"),
                            operators.comparison("updated_at", "<", "'2019-02-20'"),
                            operators.comparison("subject", "CONTAINS", "'New awesome subject'"))
                           ).all()

for ticket in tickets:
    # Get the ticket's creator
    print("Ticket creator: " + ticket.owner.name)

    # Get the ticket's status
    print("Ticket status:" + ticket.status.name)

    # Print the ticket's description
    print("Ticket description: " + ticket.description)

    # Ticket events, change_events and comments are lazy loaded.
    for comment in ticket.comments:
        if comment.created_by_user:
            print("Comment from: " + comment.created_by_user.name +
                  " says: " + comment.comment)
    for change_event in ticket.change_events:
        if change_event.created_by_user:
            print("Change by: " + str(change_event.created_by_user.name))
        for change in change_event.changes:
            print("Changed: " + str(change.name) + " from: " +
                  str(change.from_value) + " to: " + str(change.to_value))


```

# Contributing
For this repository we are enforcing the use of `Commitizen`. Respective merge requests require to follow the format created from `Commitizen`. More info can be found at: http://commitizen.github.io/cz-cli/
