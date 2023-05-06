import brownie
from brownie import (
    MinimalAuctionableNFT,
    ScatterAuction,
)
from brownie import accounts
from web3 import Web3
from random import randint

toWei = lambda x: Web3.toWei(x, 'ether')
fst = lambda xs: xs[0]
snd = lambda xs: xs[1]

def reverts(f):
    try:
        with brownie.reverts():
            f()
    except:
        return False
    return True

from_param_to_auction_house_index = {
    "bidder": 0,
    "amount": 1,
    "startTime": 2,
    "endTime": 3,
    "nftId": 4,
    "maxSupply": 5,
    "settled": 6,
    "nftContract": 7,
    "reservePrice": 8,
    "bidIncrement": 9,
    "duration": 10,
    "timeBuffer": 11,
    "nftContractBalance": 12,
    "rewardToken": 13
}

def getparam(param, auction_house):
    return auction_house.auctionData()[
        from_param_to_auction_house_index[param]
    ]

def gen_merkle_root(data):
    tree = MerkleTree()
    for x in data: tree.append_entry(x)
    return tree

def get_merkle_root_and_proofs_from_addrs_and_helds(data):
    derivs_held = [x.address + str(y) for x,y in data]
    print(derivs_held)
    tree = gen_merkle_root(derivs_held)
    proofs = [tree.prove_inclusion(x) for x in derivs_held]
    return tree.root, proofs

# Example merkle data for testing
addr_to_derivs_held = lambda: [
    (accounts[0], 3),
    (accounts[3], 1),
    (accounts[5], 7)
]

root = '0x1ac5d8fdba8b4f6e3c8d3381bee0fb781b25f4605943d1f4c16c2c501ac6bbd0'

leaves = [
    '0xd27c13c45e6a0395f716d594e1038f64611dafe9cc8b63bf820c19164a160018',
    '0xf2117fbefe2043d8ec1daf1c5ce5bbeefc106f981de674de3263b1053d94c4e8',
    '0xff98a8c4b3cef14e438c7598fe6d61b684ddbd6ffd2135f21f1b2cf596e89d64'
]

proofs = [
    [
        '0xf2117fbefe2043d8ec1daf1c5ce5bbeefc106f981de674de3263b1053d94c4e8',
        '0xff98a8c4b3cef14e438c7598fe6d61b684ddbd6ffd2135f21f1b2cf596e89d64'
    ],
    [
        '0xd27c13c45e6a0395f716d594e1038f64611dafe9cc8b63bf820c19164a160018',
        '0xff98a8c4b3cef14e438c7598fe6d61b684ddbd6ffd2135f21f1b2cf596e89d64'
    ],
    [
        '0x66464c260dc03e0bb8bf313ec3f9291032fadb210481ade182517bae30eae5b0'
    ]
]

def change_random_letter(xs):
    i = randint(0, len(xs)-1)
    new = '0'
    if xs[i] == '0': new = '1'
    new = xs[:i] + new + xs[i+1:]
    return new

def change_random_hex(addr):
    return '0x' + change_random_letter(addr[2:])

def main():
    get_merkle_root_and_proofs_from_addrs_and_helds(derivs_held)
