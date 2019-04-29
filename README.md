# clientcentral-api-python
![version](https://img.shields.io/badge/version-1.0.0-green.svg?style=for-the-badge)

# Install
```
pip install --user git+https://git.labs.epiuse.com/SWAT/clientcentral-api-python.git
```

# Features
- Object Oriented API
- Querying
- Lazy loading (Events)

# Config
The token that will be used can either be sent as an environement variable:
```bash
CC_TOKEN=<TOKEN> python3 main.py
```
Or the token can be set in the corresponding config file:
```bash
prod.yaml
qa.yaml
```
The token field should just be set example: (prod.yaml)
```yaml
base-url: "https://clientcentral.io"
token: "<MYSECRETETOKEN>"
button-ids:
  reassign-to-self: 187
```
The `prod.yaml` and `qa.yaml` files override the `prod_template.yaml` and `qa_template.yaml` configuration files. 

The previous example will override the `base-url`, you can use this if you want to run your own Client Central Instance.
This example also overrides the `button-ids`:`reassign-to-self` to `187`

# Example usage:

```python
import clientcentral.ticketformatting as tf
from clientcentral.clientcentral import ClientCentral

# Production 'false' will run on qa.cc
cc = ClientCentral(production=True)

ticket = cc.create_ticket(subject="New awesome subject" , description="this is an awesome ticket")
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
ticket.update()

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

# Production 'false' will run on qa.cc
cc = ClientCentral(production=True)
tickets = cc.query_tickets().filter_by(
            operators.and_( operators.statement("status.open"),
                            operators.comparison("workspace_id", "=", "87"),
                            operators.comparison("created_by_user.email", "=", "'thomas@labs.epiuse.com'"))
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