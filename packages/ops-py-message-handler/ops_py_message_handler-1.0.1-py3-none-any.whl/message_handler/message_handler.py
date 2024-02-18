#!/usr/bin/env python

import os
import requests
import logging
import json


###############################################################################


class MessageHandler(object):
    """
    Post a payload to a webhook url.

    ...

    Attributes
    ----------
    webhook : str
        Where the payload will be posted
    payload : dict
        The payload which will be posted
    response_code : int
        The response code of the post

    Methods
    -------
    set_payload()
        Combine heading and message to a dict
    post_payload()
        Post the payload as json to webhook
    get_response_code()
        Return the response code from the post
    """

    def __init__(self, webhook: str):
        """
        Parameters
        ----------
        webhook : str
            Where the payload will be posted
        """

        self.webhook = webhook
        self.payload = {}
        self.response_code = 0

    def set_payload(self, payload):
        """Set the provided payload as the payload

        Parameters
        ----------
        payload : dict or json
            the payload to be posted to the webhook
        """

        self.payload = payload

    def build_payload(self, **kwargs: str):
        """Build a payload of the heading and the message

        Parameters
        ----------
        kwargs : dict
            key-value pairs which will be the payload
        """

        self.payload = {}

        # Parse through every provided key-value pair and add to payload
        # Also ensure the value is converted to string before added to payload
        for k, v in kwargs.items():
            self.payload[k] = str(v).rstrip("\n")

    def post_payload(self):
        """Post the payload to the webhook

        The payload must be structured as the webhook expects. E.g. for Slack - as you have designed for the specific
        Slack Workflow in Slack Workflow Builder.

        Or like how a data payload is handled by your app: {"text":"Hello, World!"}
        More info in Slack API: https://api.slack.com/messaging and in MS Teams API docs...
        """

        if not self.webhook:
            logging.error("No webhook specified.")
            return

        if not self.payload:
            logging.warning("Posting with no payload..")
            self.payload = {}

        if isinstance(self.payload, dict):
            data = json.dumps(self.payload)
        else:
            data = self.payload

        response = requests.post(
            self.webhook, data=data,
            headers={'Content-Type': 'application/json'}
        )

        if response.status_code != 200:
            error_msg = f"Response status code: {response.status_code}. - Response text: {response.text}"
            logging.error(error_msg)
            raise ValueError(response.status_code, response.text)
        else:
            self.response_code = response.status_code
            logging.info(f"{self.response_code} - payload posted.")

    def get_response_code(self):
        return self.response_code


###############################################################################


if __name__ == '__main__':
    WEBHOOK = os.getenv("WEBHOOK")
    heading = "This is the heading"
    message = "This is the message"
    mh = MessageHandler(WEBHOOK)
    mh.build_payload(Title=heading, Text=message)
    mh.post_payload()
    response_code = mh.get_response_code()
    print(response_code)
