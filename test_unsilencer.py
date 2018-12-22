import pytest  # type: ignore
import requests
import responses  # type: ignore

import unsilencer


# There is likely a better way to use mocker to supply return values
class MockSuccessResponse(requests.Response):
    def __init__(self):
        self.status_code = 200


def test_validate_email_valid():
    assert unsilencer.validate_email("foo@bar.com") is True


def test_validate_email_invalid():
    assert unsilencer.validate_email("foo") is False
    assert unsilencer.validate_email("foo@bar") is False
    assert unsilencer.validate_email("bar.com") is False


def test_check_if_listed_returns_empty_list_when_not_found(mocker):
    mocked_check = mocker.patch("unsilencer._check_suppression_list")
    lists = unsilencer.check_if_listed("foo@bar.com")
    assert lists == []
    assert mocked_check.call_count == 3


def test_check_if_listed_returns_populated_list_when_found(mocker):
    mocked_check = mocker.patch(
        "unsilencer._check_suppression_list", return_value=MockSuccessResponse()
    )
    lists = unsilencer.check_if_listed("foo@bar.com")
    assert sorted(lists) == ["bounces", "complaints", "unsubscribes"]
    assert mocked_check.call_count == 3


def test_remove_from_list_reports_failure(mocker, capsys):
    mocked_remove = mocker.patch("unsilencer._remove_email_from_list")
    unsilencer.remove_from_list("a-list", "bar@foo.com")
    assert mocked_remove.call_count == 1
    captured = capsys.readouterr()
    assert captured.out == "Had trouble removing bar@foo.com from a-list\n"


def test_remove_from_list_reports_success(mocker, capsys):
    mocked_remove = mocker.patch(
        "unsilencer._remove_email_from_list", return_value=MockSuccessResponse()
    )
    unsilencer.remove_from_list("a-list", "foo@bar.com")
    assert mocked_remove.call_count == 1
    captured = capsys.readouterr()
    assert captured.out == "foo@bar.com removed from a-list\n"


def test_unsilencer_exits_when_email_is_invalid(mocker, capsys):
    mocker.patch("unsilencer.validate_email", return_value=False)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        unsilencer.unsilence("invalid-email")
    captured = capsys.readouterr()
    assert (
        captured.out == "The input does not appear to be a valid email address, bye!\n"
    )
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_unsilencer_reports_when_not_found(mocker, capsys):
    mocker.patch("unsilencer.validate_email", return_value=True)
    mocker.patch("unsilencer.check_if_listed", return_value=[])

    unsilencer.unsilence("bar@foo.com")

    captured = capsys.readouterr()
    assert captured.out == "bar@foo.com does not appear on any suppression list.\n"


def test_unsilencer_reports_when_found(mocker, capsys):
    mocker.patch("unsilencer.validate_email", return_value=True)
    mocker.patch("unsilencer.check_if_listed", return_value=["bounces"])
    mocker.patch("unsilencer.remove_from_list")

    unsilencer.unsilence("foo@bar.com")

    captured = capsys.readouterr()
    assert (
        captured.out == "Email address: foo@bar.com is listed on these lists:\n"
        "\tbounces\n"
        "Removing user from list now!!\n"
    )


# I know it's an antipattern to test private methods, but wanted to leave this
# example here to demonstrate the ability of testing a remote API without
# making a network call, and if the method ever changes the return value,
# this test case should also be changed or removed.
def test_check_suppression_list_for_complaint_exists():
    unsilencer.MAILGUN_API_KEY = "key-fake"
    responses.add(responses.GET, f"{unsilencer.MAILGUN_API_URL}/complaints/foo@bar.com")
    resp = unsilencer._check_suppression_list("complaints", "foo@bar.com")
    assert resp.status_code == 200
