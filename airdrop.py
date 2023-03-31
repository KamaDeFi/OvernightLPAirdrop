from web3 import Web3
from web3.gas_strategies.rpc import rpc_gas_price_strategy
import csv

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
w3.eth.set_gas_price_strategy(rpc_gas_price_strategy)

#######################################################################################################################
#                                                                                                                     #
# IMPORTANT: Please fill in these fields:                                                                             #
#                                                                                                                     #
# LP_TOKEN_AIRDROPPER_ADDRESS: Address that holds the LP tokens and will airdrop them.                                #
# LP_TOKEN_AIRDROPPER_PRIVATE_KEY: Private key of the above address as copied from MetaMask **without** a leading 0x. #                                                                                        #
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

##########################################################################
#                                                                        #
# Step 1: Approve the Airdrop contract                                   #
# https://bscscan.com/address/0x46Ea118AD231Ba378c32baf32cB931D3206ec601 #
# to spend the LP tokens.                                                #
#                                                                        #
##########################################################################

# approve(address,uint256) encoding:
# 0x095ea7b3
# <----------32 bytes address with 12 bytes leading 0s----------->
# <-----------------------32 bytes amount------------------------>
approve_data = (
    '0x095ea7b3'
    '00000000000000000000000046ea118ad231ba378c32baf32cb931d3206ec601'
    'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
)

# Create the transaction to approve the Airdrop contract to spend the LP tokens
tx_create = w3.eth.account.sign_transaction(
    {
        "nonce": w3.eth.get_transaction_count(LP_TOKEN_AIRDROPPER_ADDRESS),
        "gasPrice": w3.eth.generate_gas_price(),
        "gas": w3.eth.estimate_gas(
            { 
                'from': LP_TOKEN_AIRDROPPER_ADDRESS,
                'to': LP_TOKEN_CONTRACT_ADDRESS,
                'data': approve_data,
            }
        ),
        "to": LP_TOKEN_CONTRACT_ADDRESS,
        "data": approve_data,
    },
    f'0x{LP_TOKEN_AIRDROPPER_PRIVATE_KEY}',
)

# Send the approve transaction and wait for it to complete
tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f'Approve transaction successful with hash: {tx_receipt.transactionHash.hex()}')

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
        address = row['Address'][2:].lower()  # Remove the leading 0x and change to lowercase
        amount = int(row['LP Amount'])
        airdrop_info.append((address, amount))

##############################################################################
#                                                                            #
# Step 3: Perform the airdrop using the Airdrop contract over 4 transactions #
# of 100 addresses each (last transaction is 122 addresses).                 #
#                                                                            #
##############################################################################

# airdrop(address,address[],uint256[]) encoding:
# 0x025ff12f
# <-------32 bytes token address with 12 bytes leading 0s-------->  0
# <--------------32 bytes location of address array-------------->  32
# <--------------32 bytes location of uint256 array-------------->  64
# <---------------32 bytes length of address array--------------->  96
# <--32 bytes address array element 0 with 12 bytes leading 0s--->  128
# <--32 bytes address array element 1 with 12 bytes leading 0s--->  160
# <---------------32 bytes length of uint256 array--------------->  192
# <---------------32 bytes uint256 array element 0--------------->  224
# <---------------32 bytes uint256 array element 1--------------->  256
# Example:
# 0x025ff12f
# 000000000000000000000000acc31d29022c8eb2683597bf4c07de228ed9ea07  0
# 0000000000000000000000000000000000000000000000000000000000000060  32
# 00000000000000000000000000000000000000000000000000000000000000c0  64
# 0000000000000000000000000000000000000000000000000000000000000002  96
# 00000000000000000000000092b8f9fe69d7a0ff316de2fbeadd1a5c29f774ec  128
# 000000000000000000000000b0c06e6c5a47358ba2bede40aa750e307e50859d  160
# 0000000000000000000000000000000000000000000000000000000000000002  192
# 0000000000000000000000000000000000000000000000000b8dfd89c8029200  224
# 0000000000000000000000000000000000000000000000022362bb333e472000  256

# Split the airdrop over 4 transactions
for i in range(4):
    addresses = 100  # Each txn airdrops to 100 addresses
    if i == 3:
        addresses = 122  # Except the final txn which airdrops to 122 addresses

    uint256_array_location = 128 + 32 * addresses  # Location of the uint256 array in the data (see encoding above)

    # Data up until the 32 bytes length of address array (airdrop addresses)
    data = (
        '0x025ff12f'
        f'000000000000000000000000{LP_TOKEN_CONTRACT_ADDRESS[2:].lower()}'
        f'0000000000000000000000000000000000000000000000000000000000000060'
        f'{uint256_array_location:0{64}x}'
        f'{addresses:0{64}x}'
    )

    # Add airdrop addresses to data
    for j in range(addresses):
        address = airdrop_info[i * 1 + j][0]
        data += '000000000000000000000000' + address

    # Add 32 bytes length of uint256 array (airdrop amounts) to data
    data += f'{addresses:0{64}x}'

    # Add airdrop amounts to data
    for j in range(addresses):
        amount = airdrop_info[i * 1 + j][1]
        data += f'{amount:0{64}x}'

    # Create the airdrop transaction
    tx_create = w3.eth.account.sign_transaction(
        {
            "nonce": w3.eth.get_transaction_count(LP_TOKEN_AIRDROPPER_ADDRESS),
            "gasPrice": w3.eth.generate_gas_price(),
            "gas": w3.eth.estimate_gas(
                { 
                    'from': LP_TOKEN_AIRDROPPER_ADDRESS,
                    'to': AIRDROP_CONTRACT_ADDRESS,
                    'data': data,
                }
            ),
            "to": AIRDROP_CONTRACT_ADDRESS,
            "data": data,
        },
        f'0x{LP_TOKEN_AIRDROPPER_PRIVATE_KEY}',
    )

    # Send the airdrop transaction and wait for it to complete
    tx_hash = w3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f'Transaction {i} successful with hash: {tx_receipt.transactionHash.hex()}')
