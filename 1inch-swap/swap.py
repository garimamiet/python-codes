from web3 import Web3

from dotenv import load_dotenv

load_dotenv()
import os
import requests

rpc_url = os.getenv("rpc_url_BSC")


w3 = Web3(Web3.HTTPProvider(rpc_url))
wallet = os.getenv("account")
key = os.getenv("key")


def spender():
    url = "https://api.1inch.io/v4.0/1/approve/spender"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["address"]
    else:
        return


def allowance(token):
    url = f"https://api.1inch.io/v4.0/56/approve/allowance?tokenAddress={token}&walletAddress={wallet}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        return result["allowance"]
    else:
        return


def approve(token, amount):
    token = w3.toChecksumAddress(token)
    url = f"https://api.1inch.io/v4.0/56/approve/transaction?tokenAddress={token}&amount={amount}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()

        tx = {
            "nonce": w3.eth.get_transaction_count(wallet),
            "to": w3.toChecksumAddress(result["to"]),
            "data": result["data"],
            "gasPrice": w3.eth.gas_price,
            "gas": 100000,
        }

        signed_tx = w3.eth.account.sign_transaction(tx, key)
        tx_hsh = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
        w3.eth.wait_for_transaction_receipt(tx_hsh, timeout=120)
        return tx_hsh
    else:
        return


def swap(fromToken, toToken, amount):
    fromToken = w3.toChecksumAddress(fromToken)
    toToken = w3.toChecksumAddress(toToken)
    if int(allowance(fromToken)) < amount:
        approve(fromToken, amount)
    url = f"https://api.1inch.io/v4.0/56/swap?fromTokenAddress={fromToken}&toTokenAddress={toToken}&amount={amount}&fromAddress={wallet}&slippage=1"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        tx = {
            "nonce": w3.eth.get_transaction_count(wallet),
            "gasPrice": w3.eth.gas_price,
            "to": w3.toChecksumAddress(result["tx"]["to"]),
            "data": result["tx"]["data"],
            "gas": 200000,
        }
        # gas = w3.eth.estimate_gas(tx)
        # tx["gas"] = gas
        signed_tx = w3.eth.account.sign_transaction(tx, key)
        tx_hsh = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
        w3.eth.wait_for_transaction_receipt(tx_hsh, timeout=120)
        return tx_hsh
    else:
        return


if __name__ == "__main__":
    # example swap
    print(
        swap(
            "0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3",
            "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
            2 * 10**17,
        )
    )
