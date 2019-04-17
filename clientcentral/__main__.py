#!/usr/bin/env python
# -*- coding: utf-8 -*-

import clientcentral.ticketformatting as tf
from clientcentral.clientcentral import ClientCentral

if __name__ == "__main__":
    cc = ClientCentral(True)
    # Dummy commit 10
    ticket = cc.get_ticket_by_id("78263")
