# Instructions

Run this command:

```shell
pip install web3
```

Then modify `airdrop.py` as per the instructions at the top of that file to add the necessary addresses.

**IMPORTANT: Make sure that the address that holds the LP tokens which will perform the airdrop has enough BNB gas (0.3 BNB to be safe, but it will cost less than that). If there is not enough BNB, the script might fail half-way, which will require manual intervention changing the code and re-running.**

Then run the aidrop script:

```shell
python3 airdrop.py
```

This script will:

1. Approve the simple Airdrop contract that I created (https://bscscan.com/address/0x46Ea118AD231Ba378c32baf32cB931D3206ec601) to spend the LP tokens.
2. Read the airdrop information from `OvernightLPAirdrop.csv` (https://docs.google.com/spreadsheets/d/1tLZ0G7K6sXj9FibwqZANIF8WJ_OCxVqDI_D-nSVWo28/edit?usp=sharing)
3. Airdrop the LP tokens, split over 4 different txns, each airdropping to 100 addresses (except the 4th txn which airdrops to the remaining 122 addresses)
