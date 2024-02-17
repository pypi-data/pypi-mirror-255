import requests
import json

from xian_tools.wallet import Wallet
from xian_tools.utils import decode_dict, decode_int, decode_data, cid
from xian_tools.xian_formating import format_dictionary, check_format_of_payload
from xian_tools.xian_encoding import encode
from typing import Dict, Any


def get_nonce(node_url: str, address: str) -> int:
    """ Return next nonce """
    r = requests.post(f'{node_url}/abci_query?path="/get_next_nonce/{address}"')
    data = r.json()['result']['response']['value']

    # Data is None
    if data == 'AA==':
        return 0

    nonce = decode_int(data)
    return nonce


def get_tx(node_url: str, tx_hash: str) -> Dict[str, Any]:
    """ Return transaction with encoded content """
    r = requests.get(f'{node_url}/tx?hash=0x{tx_hash}')
    return r.json()


def decode_tx(tx: Dict[str, Any]) -> Dict[str, Any]:
    """ Return transaction with decoded content """
    if 'result' in tx:
        tx['result']['tx'] = decode_dict(tx['result']['tx'])
        tx['result']['tx_result']['data'] = decode_data(tx['result']['tx_result']['data'])
    return tx


def create_tx(
        contract: str,
        function: str,
        kwargs: Dict[str, Any],
        stamps: int,
        chain_id: str,
        private_key: str,
        nonce: int) -> Dict[str, Any]:
    """ Create transaction to be later broadcast """

    wallet = Wallet(private_key)

    payload = {
        "chain_id": chain_id if chain_id else cid(),
        "contract": contract,
        "function": function,
        "kwargs": kwargs,
        "nonce": nonce,
        "sender": wallet.public_key,
        "stamps_supplied": stamps
    }

    payload = format_dictionary(payload)
    assert check_format_of_payload(payload), "Invalid payload provided!"

    tx = {
        "payload": payload,
        "metadata": {
            "signature": wallet.sign_msg(encode(payload))
        }
    }

    tx = encode(format_dictionary(tx))
    return json.loads(tx)


def broadcast_tx(
        node_url: str,
        tx: Dict[str, Any]) -> tuple[bool, Dict[str, Any]]:
    """
    Broadcast transaction to the network
    :returns:
    - success - Boolean. True if transaction was successful
    - data - JSON. Data for checking and delivering transaction
    """

    payload = json.dumps(tx).encode().hex()
    r = requests.post(f'{node_url}/broadcast_tx_commit?tx="{payload}"')
    data = r.json()

    check = True if data['result']['check_tx']['code'] == 0 else False
    deliver = True if data['result']['deliver_tx']['code'] == 0 else False

    return (check and deliver), data
