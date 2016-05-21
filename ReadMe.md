# Balanced Mass Emailer

## Description

Many webhoster have limitation how many emails you can send per hour. By sending
a configurable amount only once per hour we can workaround this without hitting
this limitation.

Example: You need to send 3000 emails with the same content but your hoster only
allows 1000 per hour:

This script will split them into parts and will send 1000 (configurable) emails.
Then it waits one hour before sending the next 1000 ones.

So for this case it needs to run 3 hours.

## Features

* Sends only configurable amount of per hour (to comply hoster limits)
* Separate configuration file for your SMTP settings
* Configurable text and subject message
* Variables:
  * %name%
  * %email%
* Use without an external mail API like Mailchimp
* Saves the last position if you kill the application
* Displays logging messages for you to show the progress
* Gracefully exits with the amount of failed and successful sent emails
* Detect duplicate emails
* Checks for valid emails

## Usage

1. Setup an CSV file containing the following data email and name
2. Install python 3 (pre installed on Linux systems)
3. Run the script with "./FILE_NAME" on Linux or "python3 FILE_NAME"

Recommended is to run this script in [screen](https://wiki.ubuntuusers.de/Screen/)
so it doesn't end if you quit your SSH-Connection.

Example:

1. Start a named screen session: screen -S mass-emailer
2. Run the command
3. Exit the screen session: "CTR + A" and then D
4. You can then re-enter the session with "screen -r mass-emailer"
5. Close/End the screen session "CTR + D"
