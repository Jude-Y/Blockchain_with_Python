# Import dependencies
from dotenv import load_dotenv
from pprint import pprint
import subprocess
import json
import os

# Load and set environment variables
load_dotenv()
mnemonic = os.getenv('MNEMONIC')

# Import constants.py and necessary functions from bit and web3
from constants import *
from web3 import Web3
from eth_account import Account
from bit import PrivateKeyTestnet
from bit.network import NetworkAPI
from web3.middleware import geth_poa_middleware

# Connect to local host and add Middleware to support PoA
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)


# Create a function called `derive_wallets`
def derive_wallets(Mnemonic, Coin, Numderive, Format=json):
    command =f'php derive -g --mnemonic="{Mnemonic}" --coin="{Coin}" --numderive="{Numderive}" --format="json"'
    p=subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err)=p.communicate()
    p.wait()
    return json.loads(output)
    

# Create a dictionary to store the output from `derive_wallets`.
coins = {
    "btc-test": derive_wallets(mnemonic, btctest, 7),
    "eth": derive_wallets(mnemonic, eth, 4),

}

# Obtain Private Key for both ETH and BTCTest coin
eth_pk = (coins['eth'][0]['privkey'])
btctest_pk = (coins['btc-test'][1]['privkey'])



# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == 'eth':
        return Account.privateKeyToAccount(priv_key)
        
    if coin == 'btc-test':
        return PrivateKeyTestnet(priv_key)



# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == "eth":
        gas_estimate = w3.eth.estimateGas({
            "from": account.address,
            "to": to,
            "value": amount}
        )
        return {
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gas_estimate,
            "nonce": w3.eth.getTransactionCount(account.address),

            }

            
    elif coin == 'btc-test':
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, btc)])


# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    raw_tx = create_tx(coin, account, to, amount)
    signed_tx = account.sign_transaction(raw_tx)

    if coin == 'eth':
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    
    elif coin == 'btc-test':
        return NetworkAPI.broadcast_tx_testnet(signed_tx)
   

# Obtain wallet address and private key for ETH
recipient = (coins['eth'][3]['address'])
sender = priv_key_to_account(eth, eth_pk)

# Obtain wallet address and private key for BTCTEST
btcrecipient = (coins['btc-test'][2]['address'])
btcsender = priv_key_to_account(btctest, btctest_pk)


# Local PoA Ethereum transaction (make sure you are connected to Web3 by running your nodes)

# Get private key from ETH wallet that has Funds
pk = os.getenv('PRIVATE_KEY')
account_1 = Account.from_key(pk)


# Create a function to get Transacton/Hash Id for ETH

def tx_id(hashid):
    tx = w3.eth.getTransactionReceipt(send_tx),
    return tx

   
