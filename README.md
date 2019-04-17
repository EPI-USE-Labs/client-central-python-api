# clientcentral-api-python
![version](https://img.shields.io/badge/version-0.1.13-green.svg?style=for-the-badge)

# Install
```
pip install --user git+https://git.labs.epiuse.com/SWAT/clientcentral-api-python.git
```

# Example usage:
```python
from clientcentral.clientcentral import ClientCentral

cc = ClientCentral(production=True)

ticket = cc.create_ticket(subject="New awesome subject" , description="this is an awesome ticket")

```
