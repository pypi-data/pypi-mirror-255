import os
import google_takeout_email


def test_MailboxReader():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(test_dir, "test_data", "test.mbox")

    with google_takeout_email.MailboxReader(filename) as mailbox:
        messages = list(mailbox.messages)
        
        assert messages[0]["From"] == "Jarno Rantaharju <jarno.rantaharju@aalto.fi>"
        assert messages[0]["To"] == "example2 <example2@example.com>"

        assert messages[1]["From"] == "Jarno Rantaharju <jarno.rantaharju@aalto.fi>"
        assert messages[1]["To"] == "example <example@example.com>, example2 <example2@example.com>"

        assert messages[0].get_payload() == "Hello! This is a happy message!\n\n"


def test_strip_address():
    stripped = google_takeout_email.strip_address("example examplesdottir <example@example.com>")
    assert stripped == "example@example.com"


def test_parse_address_list():
    as_string = "example <example@example.com>, example2 <example2@example.com>, , example2 <example2@example.com>"
    as_list = google_takeout_email.parse_address_list(as_string)
    assert as_list[0] == "example@example.com"
    assert as_list[1] == "example2@example.com"

    assert google_takeout_email.parse_address_list("") == []
