# CheckTwoMasternodesBot

The bot is used for the [2masternodes.com](2masternodes.com) service. The bot checks the status of the nodes and show balance for address. The balance is shown from the explorer of the coin.

## Using

To use it, you need to record your telegram token in the file **CheckTwoMasternodesBot.cfg**. Example of entries in the file:

`[Global]`
`token=your_token`

The following modules must be installed:

- telegram

  `pip install python-telegram-bot --upgrade --user`

- emoji

  `pip install emoji --upgrade --user`

- requests

  `pip install requests`
