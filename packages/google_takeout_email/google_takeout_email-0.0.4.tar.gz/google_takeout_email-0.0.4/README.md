# Google Takeout Email

Contains a reader for mailbox files, MailboxReader, and utility functions for parsing
email addresses. Read from the mailbox.

The MailboxReader class functions as a context manager that opens a mailbox file. The
messages property returns an iterator of email.message objects.

The strip_address function returns the first actual email address contained in a string
and the parse_address_list returns a list of addresses in a comma separated list.

