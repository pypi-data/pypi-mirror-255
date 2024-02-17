### How to install

```python
pip install xian-tools
```

### Wallet

```python
from xian_tools.wallet import Wallet

# Create wallet from existing private key
privkey = 'ed30796abc4ab47a97bfb37359f50a9c362c7b304a4b4ad1b3f5369ecb6f7fd8'
wallet = Wallet(privkey)

# Create wallet from scratch
wallet = Wallet()

# Public key
address = wallet.public_key
print(f'address: {address}')

# Private key
privkey = wallet.private_key
print(f'private key: {privkey}')

# Sign message with private key
message = 'I will sign this message'
signed = wallet.sign_msg(message)
print(f'signed message: {signed}')
```

### Xian

```python
from xian_tools.wallet import Wallet
from xian_tools.xian import Xian

wallet = Wallet('ed30796abc4ab47a97bfb37359f50a9c362c7b304a4b4ad1b3f5369ecb6f7fd8')
xian = Xian('http://89.163.130.217:26657', wallet)

# Contract code
code = '''
token_name = Variable() # Optional

@construct
def seed():
    # Create a token with the information from fixtures/tokenInfo
    token_name.set("Test Token")

@export
def set_token_name(new_name: str):
    # Set the token name
    token_name.set(new_name)
'''

# Deploy contract on network
deploy = xian.deploy_contract("con_new_token", code)
print(f'contract deployed: {deploy}')

# Get XIAN balance
print(xian.get_balance())

# Get token balance (assuming 'con_new_token' is a token contract)
print(xian.get_balance(contract='con_new_token'))
```

### Transactions

```python
from xian_tools.wallet import Wallet
from xian_tools.xian import Xian
from xian_tools.transaction import get_nonce, create_tx, broadcast_tx
from xian_tools.utils import cid

node_url = "http://89.163.130.217:26657"

wallet = Wallet(seed='ed30796abc4ab47a97bfb37359f50a9c362c7b304a4b4ad1b3f5369ecb6f7fd8')

next_nonce = get_nonce(node_url, wallet.public_key)
print(f'next nonce: {next_nonce}')

xian = Xian(node_url, wallet)
print(f'balance: {xian.get_balance()}')

tx = create_tx(
    contract="currency",
    function="transfer",
    kwargs={
        "to": "burned",
        "amount": 100,
    },
    nonce=next_nonce,
    stamps=100,
    chain_id=cid(),
    private_key=wallet.private_key
)
print(f'tx: {tx}')

success, data = broadcast_tx(node_url, tx)
print(f'broadcast - success: {success}')
print(f'broadcast - data: {data}')

print(f'next nonce: {get_nonce(node_url, wallet.public_key)}')
print(f'balance: {xian.get_balance()}')

tx_hash = data["result"]["hash"]
print(f'tx hash: {tx_hash}')

decoded_tx = xian.get_tx(tx_hash)
print(f'get decoded tx: {decoded_tx}')
```