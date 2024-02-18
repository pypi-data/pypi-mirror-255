# Lime-Trader-SDK

Quick example:

1. Install lime-trader-sdk

```
$ pip install lime-trader-sdk
```

If you use Poetry, you can install it by running:

```
$ poetry add lime-trader-sdk
```

2. Create `credentials.json` file with next content:

```json
{
  "username": "<your_username>",
  "password": "<your_password>",
  "client_id": "<client_id>",
  "client_secret": "<client_secret>",
  "grant_type": "password",
  "base_url": "https://api.lime.co",
  "auth_url": "https://auth.lime.co"
}
```

3. Copy next code to your python script to create client and get account balances:

```python
import pprint

from lime_trader import LimeClient

client = LimeClient.from_file(file_path="credentials.json")
balances = client.account.get_balances()
pprint.pprint(balances)
```


For more information, check out the docs!