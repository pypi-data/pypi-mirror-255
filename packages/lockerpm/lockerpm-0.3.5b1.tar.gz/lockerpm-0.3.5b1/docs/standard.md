# SDK Standard

## 1. Package name

The package name of the SDK is `locker`

Example:

```
import locker
```

```
const locker = require('locker')
```

## 2. Entities name

The entity's names are singular nouns.

- Secret
- Environment
- AccessKey
- BaseAPI


## 3. Usages

### 3.1. Set locker config

Set base api, access key for the `locker`

Example:
```
import locker

locker.base_api = "https://secrets-core.locker.io"
locker.secret_access_key = "your_secret_access_key"
```


### 3.2. CRUD Methods

The CRUD methods of the object are:

```
- list()
- retrieve()
- create()
- update()
- delete()
```


### 3.3. CRUD Secret

To CRUD Secret, we have 2 options:

**Quick**

```
# List secrets object
secrets = locker.list()

# Get secret by key
secret = locker.get("GOOGLE_API_KEY")

# Get secret by key
secret = locker.get_secret("GOOGLE_API_KEY")

# Get secret object by id
secret = locker.retrieve(secret_id)

# Create new secret object
secret = locker.create(data)

# Update secret object
secret = locker.update(data)

# Delete a secret by id
locker.delete(secret_id)
```

**Standard**

```
secrets = locker.Secret.list()

secret = locker.Secret.get_secret("GOOGLE_API_KEY")

secret = locker.Secret.retrieve(secret_id)

secret = locker.Secret.create(data)

secret = locker.Secret.update(data)

locker.Secret.delete(id)
```

### 3.4. CRUD Environment

```
environments = locker.Environment.list()

environment = locker.Environment.retrieve(id)

environment = locker.Environment.create(data)

environment = locker.Environment.update(data)

locker.Secret.Environment(id)
```
