# clientcentral-api-python
![version](https://img.shields.io/badge/version-1.0.0-green.svg?style=for-the-badge)

# Install
```
pip install --user git+https://git.labs.epiuse.com/SWAT/clientcentral-api-python.git
```

# Example usage:
```python
import clientcentral.ticketformatting as tf
from clientcentral.clientcentral import ClientCentral

cc = ClientCentral(production=True)

ticket = cc.create_ticket(subject="New awesome subject" , description="this is an awesome ticket")
ticket.comment("<p>" + tf.bold("I am BOLD") + "</p>")

# Get the ticket creator
print("Ticket creator: " + ticket.owner.name)

# Get the ticket status
print("Ticket status:" + ticket.status.name)

for comment in ticket.comments:
    if comment.created_by_user:
        print("Comment from: " + comment.created_by_user.name + " says: " + comment.description)

```
