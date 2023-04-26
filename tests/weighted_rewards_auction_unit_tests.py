import pytest
from brownie import accounts, chain
from scripts.deploy_helpers import (
    deploy_weighted_rewarded_auction
)
from scripts.playground import (
    addr_to_derivs_held,
    leaves,
    proofs,
    root,
    toWei,
    fst,
    change_random_hex
)
from random import randint

def test_merkle_root_proof():
    nft, reward, auction = deploy_weighted_rewarded_auction(
        reserve_price = 0.01,
        bid_increment = 0.01,
        root=root
    )
    
    addr_to_helds = addr_to_derivs_held()

    for proof, (addr, helds) in zip(proofs, addr_to_derivs_held()):
        assert auction.checkBidderRewardableTokens(
            proof, addr.address, helds
        )

def test_merkle_root_invalid_proof():
    nft, reward, auction = deploy_weighted_rewarded_auction(
        reserve_price = 0.01,
        bid_increment = 0.01,
        root=root
    )
    
    addr_to_helds = addr_to_derivs_held()

    data = list(zip(proofs, addr_to_derivs_held())) * 10

    for proof, (addr, helds) in data:
        if helds > 0: assert not auction.checkBidderRewardableTokens(
            proof, addr.address, helds + randint(-helds, -1)
        )

    for proof, (addr, helds) in data:
        assert not auction.checkBidderRewardableTokens(
            proof, addr.address, helds + randint(1, 100)
        )
    
    for proof, (addr, helds) in data:
        assert not auction.checkBidderRewardableTokens(
            proof, change_random_hex(addr.address), helds
        )

@pytest.mark.skip
def test_merkle_root_invalid_leaf():
    assert False
