# NMI Gateway

This is the wklive implementation of nmi gateway, the original documentation of nmi is: https://secure.networkmerchants.com/gw/merchants/resources/integration/integration_portal.php#cv_variables

This package was build with the unique intention to make the integration with the gateway easy.

## Getting started

First you need to configure GOOGLE_APPLICATION_CREDENTIALS env variable to point to
your google key credentials.

```bash
GOOGLE_APPLICATION_CREDENTIALS="path/to/you/service/account/credentials.json"
```

## Doc

The library supports the next operations:

- [CustomerVault](#customer-vault)
  - [add](#add-1)
- [Plans](#plans)
  - [all](#all)
  - [id](#id)
  - [add_month_configuration](#add_month_configuration)
  - [edit_month_configuration](#edit_month_configuation)
  - [add_day_configuration](#add_day_configuration)
  - [edit_day_configuration](#edit_day_configuration)
- [Subscriptions](#subscription)
  - [add_with_custom_month_frequency_config](#add_with_custom_month_frequency_config)
  - [add_with_custom_day_frequency_config](#add_with_custom_day_frequency_config)
  - [pause](#pauseresume)
  - [cancel](#cancel)
  - [id](#id)
  - [all](#all)
- [Config](#config)
  - [get](#get)
  - [update](#update)
  - [add](#add-2)
  - [delete](#delete-1)
- [Payments](#payments)
  - [with_token](#with_token)
  - [with_customer_vault](#with_customer_vault)
  - [refund](#refund)

## Customer Vault

Handle customer vault operations

### add-1

Create a new customer vault with the provided id (this id is then used by other methods of this library as user_id)

```python
# import library
from wknmi.customer_vault import CustomerVault

# init CustomerVault
customerVault = CustomerVault(url="https://nmi-server-orkrbzqvda-uc.a.run.app", org="testOrg4")
# add user
customerVault.add({
    "id": "testId113233",
    "token": "00000000-000000-000000-000000000000",
    "billing_id": "",
    "billing_info":{
        "first_name": "",
        "last_name": "",
        "address1": "",
        "city": "",
        "state": "",
        "zip": "",
        "country": "",
        "phone": "",
        "email": ""
    }
    })

```

### edit

Edit customer vault with the provided id (this id is then used by other methods of this library as user_id)

```python
# import library
from wknmi.customer_vault import CustomerVault

# init CustomerVault
customerVault = CustomerVault(url="https://nmi-server-orkrbzqvda-uc.a.run.app", org="testOrg4")
# add user
customerVault.edit({
    "id": "testId113233",
    "billing_id": "",
    "billing_info":{
        "first_name": "",
        "last_name": "",
        "address1": "",
        "city": "",
        "state": "",
        "zip": "",
        "country": "",
        "phone": "",
        "email": ""
    }
    })

```

### delete

Delete customer vault with the provided id (this id is then used by other methods of this library as user_id)

```python
# import library
from wknmi.customer_vault import CustomerVault

# init CustomerVault
customerVault = CustomerVault(url="https://nmi-server-orkrbzqvda-uc.a.run.app", org="testOrg4")
# add user
customerVault.delete(id="testId113233")

```

## Plans

Handles plan operations with the nmi api

### all

Get all plans created plans in the organization

```python
# import library
from wknmi.plans import Plans

# init
plan = Plans(url="https://nmi-server-orkrbzqvda-uc.a.run.app", org="testOrg4")

# get plans
plan.all()
```

### id

Get plan id information

```python
# get swzshoppingonly plan information
plan.id("swzshoppingonly")
```

### add_month_configuration

Create a new plan using month setup

```python
# create plan
plan.add_month_configuration({
    "custom_plan": {
        "plan_amount": "10.00",
        "plan_name": "test",
        "plan_id": "testtset",
        "month_frequency": "1",
        "day_of_month": "1",
        "plan_payments": "0"
    }
})
```

### edit_month_configuation

Edit plan using month configuration

```python
# edit month configuration plan
plan.edit_month_configuration({
    "custom_plan": {
        "plan_amount": "10.00",
        "plan_name": "test",
        "plan_id": "testtset",
        "month_frequency": "1",
        "day_of_month": "1",
        "plan_payments": "0"
    }
})
```

### add_day_configuration

Create a new plan using day setup

```python
# create a plan using day configuration
plan.add_day_configuration({
    "custom_plan": {
        "plan_amount": "10.00",
        "plan_name": "test",
        "plan_id": "testtsetts",
        "day_frequency": "1",
        "plan_payments": "0"
    }
})
```

### edit_day_configuration

Edit a plan using day setup

```python
# edit a plan using day configuration
plan.edit_day_configuration({
    "custom_plan": {
        "plan_amount": "20.00",
        "plan_name": "test",
        "plan_id": "testtsetts",
        "day_frequency": "1",
        "plan_payments": "0"
    }
})
```

## Subscription

Handles subscriptions using the nmi api

### add_with_custom_month_frequency_config

Assign a subscriptions to the user_id (customer vault).
if total_amount is set to 0, the method will behave as a normal subscription and the user will be charged according to the custom_subscription info object. But if total_amount is set to a value greater that 0 the user will be charged by that amount

```python
# import library
from wknmi.subscriptions import Subscriptions

# init
subsObj = Subscriptions(url="https://nmi-server-orkrbzqvda-uc.a.run.app",org="testOrg4")

# assign subscription to custumer vault
subsObj.add_with_custom_month_frequency_config({
    "user_id": "1",
    "order_id": "test",
    "total_amount": "0", # 0 for subscription without an addition sale amount
    "custom_subscription_info": {
        "plan_id": "test",
        "plan_amount": "10.00",
        "plan_name": "test",
        "month_frequency": "1",
        "day_of_month": "1",
        "plan_payments": "0"
    }
})
```

### add_with_custom_day_frequency_config

Assign a subscriptions to the user_id (customer vault).
if total_amount is set to 0, the method will behave as a normal subscription and the user will be charged according to the custom_subscription info object. But if total_amount is set to a value greater that 0 the user will be charged by that amount

```python

# assign subscription to custumer vault
subsObj.add_with_custom_day_frequency_config({
    "user_id": "1",
    "org": "testOrg",
    "order_id": "testRef",
    "total_amount": "0",# 0 for subscription without an addition sale amount
    "custom_subscription_info": {
        "plan_payments": "15",
        "plan_amount": "6",
        "day_frequency": "1"
    }
})
```

### Pause/Resume

Pause subscription

```python
#pause subscription
subscription_id = "your subscription id"
pause = "true" # true to pause/false to resume
subsObj.pause(subscription_id, "true")
```

### Cancel

Cancel a subscripion

```python
subscription_id = "your subscription id"
result = subsObj.cancel(subscription_id)
```

### by_user_id

Get all subscriptions of user_id

```python
#get subscriptions of user id
user_id = "your user id"
result = subsObj.by_user_id(user_id)
```

## Config

Handles creations of the merchants

### get

Get merchant information

```python
# import library
from wknmi.config import Config

# init
Config(url="http://127.0.0.1:8000",org="testOrg4")

# get merchant configuration
configObj.get()
```

### update

Update merchant information

```python
# edit merchant information
configObj.update({
    "store_id": 2342311,
    "environment_active": "sandbox",
    "org":"testOrg4",
    "production_env": {
        "token": ""
    },
    "sandbox_env": {
        "token": ""
    },
    "secret_token": "",
    "merchant_orchestrator_url":"http://",
    "merchant_id":"123",
    "merchant_signature":"123"
})
```

### add

Create a new merchant

```python
# add a new merchant
configObj.add({
    "store_id": 234232211,
    "environment_active": "sandbox",
    "org":"testOrg5",
    "production_env": {
        "token": "4QaH5w77U2k843fu68EuB34c4M5KJ7r3"
    },
    "sandbox_env": {
        "token": "4QaH5w77U2k843fu68EuB34c4M5KJ7r3"
    },
    "secret_token": "4QaH5w77U2k843fu68EuB34c4M5KJ7r3",
    "merchant_orchestrator_url":"http://",
    "merchant_id":"123",
    "merchant_signature":"123"
})
```

### delete

Delete a merchant

```python
configObj.delete("testOrg5")
```

## Payments

Handles nmi payments

### with_token

```python
# import library
from wknmi.payment import Pay

# init
pay = Pay(url="https://nmi-server-orkrbzqvda-uc.a.run.app", org="testOrg")

# fill payment data
result = pay.with_token(
    {
        "token": "00000000-000000-000000-000000000000",
        "total": "11",
        "billingInfo": {
            "first_name": "",
            "last_name": "",
            "address1": "",
            "city": "",
            "state": "",
            "zip": "",
            "country": "",
            "phone": "",
            "email": "",
            "company": "",
            "address2": "",
            "fax": "",
            "shipping_id": "",
            "shipping_address1": "",
            "shipping_address2": "",
            "shipping_city": "",
            "shipping_country": "",
            "shipping_zip": "",
            "shipping_state": "",
            "shipping_first_name": "",
            "shipping_last_name": "",
            "shipping_phone": "",
            "shipping_email": ""
        },
    }
)
```

### with_customer_vault

```python
# import library
from wknmi.payment import Pay

# init
pay = Pay(url="https://nmi-server-orkrbzqvda-uc.a.run.app", org="testOrg")

# fill payment data
pay.with_customer_vault({
    "customerVault": "982f128f-8e77-4ed9-a495-1b708f79b8e2",
    "total": "11",
    "billingInfo": {
        "first_name": "",
        "last_name": "",
        "address1": "",
        "city": "",
        "state": "",
        "zip": "",
        "country": "",
        "phone": "",
        "email": "",
        "company": "",
        "address2": "",
        "fax": "",
        "shipping_id": "",
        "shipping_address1": "",
        "shipping_address2": "",
        "shipping_city": "",
        "shipping_country": "",
        "shipping_zip": "",
        "shipping_state": "",
        "shipping_first_name": "",
        "shipping_last_name": "",
        "shipping_phone": "",
        "shipping_email": ""
    },
})
```

### refund

```python
# import library
from wknmi.payment import Pay

# init
pay = Pay(url="https://nmi-server-orkrbzqvda-uc.a.run.app", org="testOrg")

# fill payment data
pay.refund("9192863564")
```
