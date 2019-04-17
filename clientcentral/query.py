# query().filter_by(Comparison("created_by_user.name", "=", "name"))
import requests
import json
from clientcentral.ticket import Ticket

class QueryTickets:
    _query = None

    base_url = None
    token = None

    config = None
    production = None

    def __init__(self, base_url, token, config, production):
        self._query = ""
        self.base_url = base_url
        self.token = token
        self.config = config
        self.production = production

    def filter_by(self, arg):
        self._query ="&filter=" + str(arg)
        return self

    def all(self):
        url = self.base_url + "/api/v1/tickets.json?" + self.token
        payload = self._query + "&select=created_at,updated_at,id"
        response = requests.get(url + payload)
        print(response.text)

        response.raise_for_status()

        result = json.loads(response.text)
        tickets = []
        for ticket_in_data in result["data"]:
            ticket = Ticket(
                base_url=self.base_url,
                token=self.token,
                ticket_id=str(ticket_in_data["id"]),
                config=self.config,
                production=self.production)
            tickets.append(ticket)

        return tickets


def and_(*argv: str):
    result = ""
    for i, arg in enumerate(argv):
        if i < len(argv) - 1:
            result += str(arg) + "%20AND%20"
        else:
            result += str(arg)

    return result


def not_(arg: str):
    return "NOT " + str(arg)


def comparison(left, operator, right):
    return str(left) + "%20" + str(operator) + "%20" + str(right)