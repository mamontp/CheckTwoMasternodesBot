# CheckTwoMasternodesBot

The bot is used for the [2masternodes.com](2masternodes.com) service. The bot checks the status of the nodes and show balance for address. The balance is shown from the explorer of the coin.

## Using

To use it, you need to record your telegram token in the file **CheckTwoMasternodesBot.cfg**. Example of entries in the file:

```[Global]
token=your_token

listen=XX.XX.XX.XX 		<- The listen address

port=8443

webhook_url=XX.XX.XX.XX	<- The webhook_url should be the actual URL of your webhook.
```
### Using Webhook
If you are using Webhook, then you need to generate certificates and put them along the `cert/` path. 

#### Creating a self-signed certificate using OpenSSL

To create a self-signed SSL certificate using openssl, run the following command:

`openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 3650 -out cert.pem`

The openssl utility will ask you a few details. **Make sure you enter the correct FQDN!** If your server has a domain, enter the full domain name here (eg. sub.example.com). If your server only has an IP address, enter that instead. If you enter an invalid FQDN (Fully Qualified Domain Name), you won't receive any updates from Telegram but also won't see any errors!

More information can be found in the article: [Webhooks](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks)

## Sending a notification that the service [(2masternodes.com)](2masternodes.com) has sent the received coins to the user's address
To receive notifications, you need to place a script `NotifyTransaction.py` in the `crontab`. Example:

`15 * * * * /home/user_name/CheckTwoMasternodesBot/NotifyTransaction.py -p /home/user_name/CheckTwoMasternodesBot >> ~/CheckTwoMasternodesBot/NotifyTransaction.out 2>&1`

File `LastCheckTime.txt` stores the time of the last check. Example:
`2018-10-15 09:15:01.438180`

## Requirements

The following modules must be installed:

- telegram

  `pip install python-telegram-bot --upgrade --user`

- emoji

  `pip install emoji --upgrade --user`

- requests

  `pip install requests`
