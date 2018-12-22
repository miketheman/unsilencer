import os
import re
import sys

import requests

MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
MAILGUN_DOMAIN_NAME = os.environ.get("MAILGUN_DOMAIN_NAME")

MAILGUN_API_BASE_URL = "https://api.mailgun.net/v3"
MAILGUN_API_URL = f"{MAILGUN_API_BASE_URL}/{MAILGUN_DOMAIN_NAME}"
MAILGUN_SUPPRESSION_LISTS = "bounces", "complaints", "unsubscribes"


def validate_email(input: str) -> bool:
    matches = re.match(r"[^@]+@[^@]+\.[^@]+", input)
    if matches:
        return True
    return False


def check_if_listed(email_address: str) -> list:
    listings = {}
    # iterate through all 3 functions
    for suppression_list in MAILGUN_SUPPRESSION_LISTS:
        response = _check_suppression_list(suppression_list, email_address)
        if response.status_code == 200:
            listings[suppression_list] = response

    # I know I'm throwing away the response value from the dict here,
    # but I wanted to keep it part of the payload for inspection if needed.
    lists = [key for key, _value in listings.items()]
    return lists


def remove_from_list(suppression_list: str, email_address: str):
    response = _remove_email_from_list(suppression_list, email_address)
    if response.status_code != 200:
        print(f"Had trouble removing {email_address} from {suppression_list}")
    else:
        print(f"{email_address} removed from {suppression_list}")


def _check_suppression_list(
    suppression_list: str, email_address: str
) -> requests.models.Response:  # pragma: no cover
    return requests.get(
        f"{MAILGUN_API_URL}/{suppression_list}/{email_address}",
        auth=("api", MAILGUN_API_KEY),
    )


def _remove_email_from_list(
    suppression_list: str, email_address: str
) -> requests.models.Response:  # pragma: no cover
    return requests.delete(
        f"{MAILGUN_API_URL}/{suppression_list}/{email_address}",
        auth=("api", MAILGUN_API_KEY),
    )


def unsilence(email_address: str):
    if not validate_email(email_address):
        print("The input does not appear to be a valid email address, bye!")
        sys.exit(1)

    lists = check_if_listed(email_address)

    if len(lists) == 0:
        print(f"{email_address} does not appear on any suppression list.")
    else:
        print(f"Email address: {email_address} is listed on these lists:")
        print("\t" + ",".join(lists))

        print("Removing user from list now!!")
        for suppression_list in lists:
            remove_from_list(suppression_list, email_address)


if __name__ == "__main__":  # pragma: no cover
    try:
        input = sys.argv[1]
    except IndexError:
        print("You must pass an email address!")
        sys.exit(1)

    unsilence(input)
