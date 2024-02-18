# Official Python sdk for [Original](https://getoriginal.com) API

## Table of Contents

- [About Original](#-about-original)
- [Getting Started](#-getting-started)
- [Documentation](#-documentation)
  - [Initialization](#initialization)
  - [User](#user)
  - [Asset](#asset)
  - [Collection](#collection)
  - [Transfer](#transfer)
  - [Burn](#burn)
  - [Deposit](#deposit)

## 📝 About Original

You can request access for an Original account at our [Request Access](https://getoriginal.com/contact-us/) page.

## ✨ Getting started

Install Original

```bash
$ pip install original-sdk
```

## 📚 Documentation

### Initialization

The Original SDK is set up to expose the Original API.

Read the full [Original API documentation](https://docs.getoriginal.com).

```python

from original_sdk import OriginalClient

```

Create a new instance of the Original client by passing in your api key and api key secret.

```python
client = OriginalClient(api_key='YOUR_API_KEY', api_secret='API_KEY_SECRET')
```

### User

The user methods exposed by the sdk are used to create and retrieve users from the Original API.

```python
# create a new user
new_user_uid = client.create_user(email='YOUR_EMAIL', client_id='YOUR_CLIENT_ID' )

# gets a user by uid, will throw a 404 Not Found error if the user does not exist
# returns user data
user = client.get_user(new_user_uid)

# gets a user by email or client_id
# will return user data type if the user exists, otherwise will return null
user_by_email = client.get_user_by_email('YOUR_EMAIL')

user_by_client_id = client.get_user_by_client_id('YOUR_CLIENT_ID')
```

### Asset

The asset methods exposed by the sdk are used to create (mint) assets and retrieve assets from the Original API.

```python
# prepare the new asset params
new_asset_data = {
    "user_uid": "324167489835",
    "client_id": "client_id_1",
    "collection_uid": "221137489875",
    "data": {
        "name": "Dave Starbelly",
        "unique_name": True,
        "image_url": "https://storage.googleapis.com/opensea-prod.appspot.com/puffs/3.png",
        "store_image_on_ipfs": True,
        "description": "Friendly OpenSea Creature that enjoys long swims in the ocean.",
        "external_url": "https://openseacreatures.io/3",
        "attributes": [
            {
                "trait_type": "Base",
                "value": "Starfish"
            },
            {
                "trait_type": "Eyes",
                "value": "Big"
            },
            {
                "trait_type": "Aqua Power",
                "display_type": "boost_number",
                "value": 40
            },
            {
                "trait_type": "Stamina Increase",
                "display_type": "boost_percentage",
                "value": 10
            },
        ]
    }
}

# create a new asset
# returns the uid of the newly created asset
new_asset_uid = client.create_asset(**new_asset_data)

# gets an asset by uid, will throw a 404 Not Found error if the asset does not exist
asset = client.get_asset(new_asset_uid)

# gets assets by the owner uid
# will return a list of assets owned by the user
assets = client.get_asset_by_user_uid(user_uid)

# prepare the edit asset params
edit_asset_data = {
    "data": {
        "name": "Dave Starbelly Edited",
        "unique_name": True,
        "image_url": "https://storage.googleapis.com/opensea-prod.appspot.com/puffs/3.png",
        "description": "Friendly OpenSea Creature that enjoys long swims in the ocean. Edited",
        "attributes": [
            {
                "trait_type": "Base",
                "value": "Starfish"
            },
        ]
    }
}

# edits an asset by uid, by passing in the new asset data
# returns success true or false
client.edit_asset(new_asset_uid, **edit_asset_data)
```

### Collection

The collection methods exposed by the sdk are used to retrieve collection details from the Original API.

```python
# gets a collection by uid, will throw a 404 Not Found error if the collection does not exist
# returns collection detail
collection = client.get_collection('221137489875')
```

### Transfer

The transfer methods exposed by the sdk are used to transfer assets from one user to another wallet.

```python
# create a transfer of an asset, by passing in transfer details
# returns the uid of the newly created transfer
transfer_uid = client.create_transfer(
  asset_uid = asset_uid,
  from_user_uid = user_uid,
  to_address = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
)

# gets a transfer by uid, will throw a 404 Not Found error if the transfer does not exist
transfer = client.get_transfer(transfer_uid)

# gets transfers by user uid
# will return a list of transfers for the user
transfers = client.get_transfers_by_user_uid(user_uid)
```

### Burn

The burn methods exposed by the sdk are used to burn assets from a user's wallet.

```python
# create a burn of an asset
# returns the uid of the newly created burn
burn_uid = client.create_burn(
  asset_uid=asset_uid,
  from_user_uid=user_uid,
)

# gets a burn by uid, will throw a 404 Not Found error if the burn does not exist
burn = client.get_burn(burn_uid)

# gets burns by user uid
burns = client.get_burn_by_user_uid(user_uid)
```


### Deposit

The deposit methods exposed by the sdk are used to return the details for depositing assets.

```python
# gets deposit details for a user
# returns the deposit details
deposit = client.get_deposit(user_uid)
```
