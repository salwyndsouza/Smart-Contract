import time
import json
import web3
from eth_account import Account
from web3.auto import w3
from web3.providers.websocket import WebsocketProvider
from web3 import Web3
from solc import compile_standard

with open("Contract.sol") as c:
 contractText=c.read()
with open(".pk") as pkfile:
 privateKey=pkfile.read()
with open(".infura") as infurafile:
 infuraKey=infurafile.read()

compiled_sol = compile_standard({
 "language": "Solidity",
 "sources": {
  "Greeter.sol": {
   "content": contractText
  }
 },
 "settings":
 {
  "outputSelection": {
   "*": {
    "*": [
     "metadata", "evm.bytecode"
     , "evm.bytecode.sourceMap"
    ]
   }
  }
 }
})
bytecode = compiled_sol['contracts']['Greeter.sol']['Greeter']['evm']['bytecode']['object']
abi = json.loads(compiled_sol['contracts']['Greeter.sol']['Greeter']['metadata'])['output']['abi']
W3 = Web3(WebsocketProvider('wss://ropsten.infura.io/ws/v3/%s'%infuraKey))
account1=Account.from_key(privateKey);
address1=account1.address
Greeter = W3.eth.contract(abi=abi, bytecode=bytecode)

nonce = W3.eth.getTransactionCount(address1)
#diagnostics
#print(nonce)
# Submit the transaction that deploys the contract
tx_dict = Greeter.constructor().buildTransaction({
'chainId': 3,
'gas': 1200000,
'gasPrice': w3.toWei('30', 'gwei'),
'nonce': nonce,
'from':address1
})

signed_txn = W3.eth.account.sign_transaction(tx_dict, private_key=privateKey)

print("Deploying the Smart Contract")
result = W3.eth.sendRawTransaction(signed_txn.rawTransaction)

tx_receipt = None#W3.eth.getTransactionReceipt(result)

count = 0
while tx_receipt is None and (count < 300):
  time.sleep(1)
  try:
    tx_receipt = W3.eth.getTransactionReceipt(result)
  except:
    print('.')

if tx_receipt is None:
  print (" {'status': 'failed', 'error': 'timeout'} ")

print("\nContract address is:",tx_receipt.contractAddress)

greeter = W3.eth.contract(
  address=tx_receipt.contractAddress,
  abi=abi
)
print("Output from greet()")
print(greeter.functions.greet().call())

