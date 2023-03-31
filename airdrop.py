from web3 import Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy
import csv

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)
CHAIN_ID = w3.eth.chain_id

#######################################################################################################################
#                                                                                                                     #
# IMPORTANT: Please fill in these fields:                                                                             #
#                                                                                                                     #
# LP_TOKEN_AIRDROPPER_ADDRESS: Address that holds the LP tokens and will airdrop them                                 #
# LP_TOKEN_AIRDROPPER_PRIVATE_KEY: Private key of the above address as copied from MetaMask **without** a leading 0x, #
# exactly as copied from Metamask                                                                                     #
#                                                                                                                     #
# IMPORTANT: Please make sure that the airdropping address that holds the LP tokens has enough BNB gas for the        #
# airdrop (0.3 BNB to be safe), otherwise this script might fail half-way, which will require manual intervention     #
# changing the code and re-running.                                                                                   #
#                                                                                                                     #
#######################################################################################################################

LP_TOKEN_AIRDROPPER_ADDRESS = 'PUT_LP_TOKEN_AIRDROPPER_ADDRESS_HERE'
LP_TOKEN_AIRDROPPER_PRIVATE_KEY = 'PUT_LP_TOKEN_AIRDROPPER_PRIVATE_KEY_HERE'

# Other constants
LP_TOKEN_CONTRACT_ADDRESS = '0xaCC31d29022C8Eb2683597bF4c07De228Ed9EA07'
AIRDROP_CONTRACT_ADDRESS = '0x46Ea118AD231Ba378c32baf32cB931D3206ec601'
APPROVE_ABI = '[{"stateMutability":"nonpayable","type":"function","name":"approve","inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]}]'
AIRDROP_ABI = '[{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"address[]","name":"addresses","type":"address[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"name":"airdrop","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
MAX_APPROVAL = 115792089237316195423570985008687907853269984665640564039457584007913129639935

##########################################################################
#                                                                        #
# Step 1: Approve the Airdrop contract                                   #
# https://bscscan.com/address/0x46Ea118AD231Ba378c32baf32cB931D3206ec601 #
# to spend the LP tokens.                                                #
#                                                                        #
##########################################################################

lp_token_contract = w3.eth.contract(address=LP_TOKEN_CONTRACT_ADDRESS, abi=APPROVE_ABI)
approve_txn = lp_token_contract.functions.approve(AIRDROP_CONTRACT_ADDRESS, MAX_APPROVAL).build_transaction(
    {
        'chainId': CHAIN_ID,
        'from': LP_TOKEN_AIRDROPPER_ADDRESS,
        'nonce': w3.eth.get_transaction_count(LP_TOKEN_AIRDROPPER_ADDRESS),
        'gasPrice': w3.eth.generate_gas_price(),
    }
)
approve_txn.update({'gas': w3.eth.estimate_gas(approve_txn)})
approve_txn_signed = w3.eth.account.sign_transaction(
    approve_txn,
    f'0x{LP_TOKEN_AIRDROPPER_PRIVATE_KEY}',
)
approve_tx_hash = w3.eth.send_raw_transaction(approve_txn_signed.rawTransaction)
approve_tx_receipt = w3.eth.wait_for_transaction_receipt(approve_tx_hash)
print(f'Approve transaction successful with hash: {approve_tx_receipt.transactionHash.hex()}')

########################################################################################################
#                                                                                                      #
# Step 2: Read the airdrop data from the CSV file                                                      #
# https://docs.google.com/spreadsheets/d/1tLZ0G7K6sXj9FibwqZANIF8WJ_OCxVqDI_D-nSVWo28/edit?usp=sharing #
#                                                                                                      #
########################################################################################################

airdrop_info = []
with open('OvernightLPAirdrop.csv', 'r') as f:
    csv_reader = csv.DictReader(f, delimiter=',')
    for row in csv_reader:
        address = row['Address']
        amount = int(row['LP Amount'])
        airdrop_info.append((address, amount))

##############################################################################
#                                                                            #
# Step 3: Perform the airdrop using the Airdrop contract over 4 transactions #
# of 100 addresses each (last transaction is 122 addresses).                 #
#                                                                            #
##############################################################################

# Split the airdrop over 4 transactions
for i in range(4):
    addresses = 100  # Each txn airdrops to 100 addresses
    if i == 3:
        addresses = 122  # Except the final txn which airdrops to 122 addresses
    infos = airdrop_info[i * 100:(i * 100) + addresses]
    addresses_list = [info[0] for info in infos]
    amounts_list = [info[1] for info in infos]
    airdrop_contract = w3.eth.contract(address=AIRDROP_CONTRACT_ADDRESS, abi=AIRDROP_ABI)
    airdrop_txn = airdrop_contract.functions.airdrop(LP_TOKEN_CONTRACT_ADDRESS, addresses_list, amounts_list).build_transaction(
        {
            'chainId': CHAIN_ID,
            'from': LP_TOKEN_AIRDROPPER_ADDRESS,
            'nonce': w3.eth.get_transaction_count(LP_TOKEN_AIRDROPPER_ADDRESS),
            'gasPrice': w3.eth.generate_gas_price(),
        }
    )
    airdrop_txn.update({'gas': w3.eth.estimate_gas(airdrop_txn)})
    airdrop_txn_signed = w3.eth.account.sign_transaction(
        airdrop_txn,
        f'0x{LP_TOKEN_AIRDROPPER_PRIVATE_KEY}',
    )
    airdrop_tx_hash = w3.eth.send_raw_transaction(airdrop_txn_signed.rawTransaction)
    airdrop_tx_receipt = w3.eth.wait_for_transaction_receipt(airdrop_tx_hash)
    print(f'Airdrop transaction {i} successful with hash: {airdrop_tx_receipt.transactionHash.hex()}')
