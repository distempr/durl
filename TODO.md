# durl todo

- Update get command to use curl -I/-i and just curl-like output
- Add cleanup script
  - Run using systemd timer every hour with randomised delay of 1 minute
- Update update command so it can update description, expires
- Handle empty URL
