import requests
import xian_tools.utils as utl
import xian_tools.transaction as tr

from xian_tools.wallet import Wallet
from typing import Dict, Any


class Xian:
    def __init__(self, node_url: str, wallet: Wallet = None):
        self.wallet = wallet if wallet else Wallet()
        self.node_url = node_url

    def get_tx(self, tx_hash: str) -> Dict[str, Any]:
        """ Return transaction with decoded content """
        encoded_tx = tr.get_tx(self.node_url, tx_hash)
        return tr.decode_tx(encoded_tx)

    def get_balance(
            self,
            address: str = None,
            contract: str = 'currency') -> int | float:
        """ Return balance for given address and token contract """

        address = address if address else self.wallet.public_key

        r = requests.get(f'{self.node_url}/abci_query?path="/get/{contract}.balances:{address}"')
        balance_byte_string = r.json()['result']['response']['value']

        # Decodes to 'None'
        if balance_byte_string == 'AA==':
            return 0

        try:
            balance = utl.decode_int(balance_byte_string)
            return int(balance)
        except:
            balance = utl.decode_float(balance_byte_string)
            return balance

    def send_tx(
            self,
            contract: str,
            function: str,
            kwargs: dict,
            stamps: int = 500,
            chain_id: str = None) -> tuple[bool, str]:
        """
        Send a transaction to the network
        :returns:
        - success - Boolean. True if successful
        - data - String. Transaction hash
        """

        tx = tr.create_tx(
            contract=contract,
            function=function,
            kwargs=kwargs,
            stamps=stamps,
            chain_id=chain_id,
            private_key=self.wallet.private_key,
            nonce=tr.get_nonce(
                self.node_url,
                self.wallet.public_key
            )
        )

        success, data = tr.broadcast_tx(self.node_url, tx)
        return success, data['result']['hash']

    def send(
            self,
            amount: [int, float, str],
            to_address: str,
            token: str = "currency",
            stamps: int = 100,
            chain_id: str = None) -> tuple[bool, str]:
        """
        Send a token to a given address
        :returns:
        - success - Boolean. True if successful
        - data - String. Transaction hash
        """

        kwargs = {"amount": float(amount), "to": to_address}
        return self.send_tx(token, "transfer", kwargs, stamps, chain_id)

    def approve(
            self,
            contract: str,
            token: str = "currency",
            amount: int | float | str = 9000000000000,
            chain_id: str = None) -> tuple[bool, str]:
        """ Approve smart contract to spend max token amount """

        kwargs = {"amount": float(amount), "to": contract}
        return self.send_tx(token, "approve", kwargs, 50, chain_id)

    def get_approved_amount(self):
        pass

    def get_contract_data(self):
        pass

    def deploy_contract(
            self,
            name: str,
            code: str,
            stamps: int = 1000,
            chain_id: str = None) -> tuple[bool, str]:
        """
        Deploy a contract to the network
        :returns:
        - success - Boolean. True if successful
        - data - String. Transaction hash
        """

        tx = tr.create_tx(
            contract="submission",
            function="submit_contract",
            kwargs={
                "name": name,
                "code": code,
            },
            nonce=tr.get_nonce(
                self.node_url,
                self.wallet.public_key
            ),
            stamps=stamps,
            chain_id=chain_id,
            private_key=self.wallet.private_key,
        )

        success, data = tr.broadcast_tx(self.node_url, tx)
        return success, data['result']['hash']
