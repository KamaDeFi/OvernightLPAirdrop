# Instructions

Run this command:

```shell
pip install web3
```

Then modify `airdrop.py` as per the instructions at the top of that file to add the necessary addresses.

**IMPORTANT: Make sure that the address that holds the LP tokens which will perform the airdrop has enough BNB gas (0.3 BNB to be safe, but it will cost less than that). If there is not enough BNB, the script might fail half-way, which will require manual intervention changing the code and re-running.**

Then run the airdrop script:

```shell
python3 airdrop.py
```

This script will:

1. Approve the simple Airdrop contract that I created (https://bscscan.com/address/0x46Ea118AD231Ba378c32baf32cB931D3206ec601) to spend the LP tokens
2. Read the airdrop information from `OvernightLPAirdrop.csv` (https://docs.google.com/spreadsheets/d/1tLZ0G7K6sXj9FibwqZANIF8WJ_OCxVqDI_D-nSVWo28/edit?usp=sharing)
3. Airdrop the LP tokens, split over 4 different txns, each airdropping to 100 addresses (except the 4th txn which airdrops to the remaining 122 addresses)

If successful, the output will look like this (with different txn hashes):

```shell
python3 airdrop.py
Approve transaction successful with hash: 0x0fb505ba186b8504a4b079bc8ab968ea7505ca1d7bc35090e3d3e64481bdc87c
Airdrop transaction 0 successful with hash: 0x54388272e7c78d5b02bcddcfcfbc7870f7b3646ae8f7c23ddef10479f15ba8f7
Airdrop transaction 1 successful with hash: 0xe7d54e53bb81a0e42cda01a0f4f8a6ff9c19461fdc00fe9c97eec7453e204321
Airdrop transaction 2 successful with hash: 0xfde4edea07c54728ade76cc241c069aed95ecfefd59ba707b36be7be79d21a25
Airdrop transaction 3 successful with hash: 0xfc2dd0c4620420fd205ac4d3764f8931c9467f728aeaf3f70d76196b0441e42a
```
