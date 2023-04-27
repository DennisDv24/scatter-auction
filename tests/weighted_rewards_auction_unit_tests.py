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
    change_random_hex,
    reverts
)
from random import randint

ZERO = f'0x{"0"*40}'

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

def test_empty_rewards_claim():
    nft, reward, auction = deploy_weighted_rewarded_auction(
        reserve_price = 0.01,
        bid_increment = 0.01,
        root=root
    )
    
    addr_to_helds = addr_to_derivs_held()

    rewarded_bidder = addr_to_helds[1][0]
    rewarded_bidder_proof = proofs[1]
    rewarded_bidder_holds = addr_to_helds[1][1]

    bidder = accounts[1]

    assert reward.balanceOf(bidder) == 0
    assert reward.balanceOf(rewarded_bidder) == 0

    assert reverts(lambda: auction.claimRewardTokensBasedOnShares(
        [0], 0, {'from': bidder}
    ))
    assert reverts(lambda: auction.claimRewardTokensBasedOnShares(
        rewarded_bidder_proof, rewarded_bidder_holds, {'from': bidder}
    ))

    assert reward.balanceOf(bidder) == 0
    assert reward.balanceOf(rewarded_bidder) == 0

def test_reward_claim_without_tokens_in_contract():
    nft, reward, auction = deploy_weighted_rewarded_auction(
        reserve_price = 0.1,
        bid_increment = 0.05,
        root=root
    )
    
    addr_to_helds = addr_to_derivs_held()

    rewarded_bidder = addr_to_helds[1][0]
    rewarded_bidder_proof = proofs[1]
    rewarded_bidder_holds = addr_to_helds[1][1]

    bidder = accounts[1]
    
    auction.createBid(1, {'from': bidder, 'value': toWei(0.1)})
    auction.createBid(1, {'from': rewarded_bidder, 'value': toWei(0.25)})
    auction.createBid(1, {'from': bidder, 'value': toWei(0.3)})
    
    expected_rewards = {}
    expected_rewards[bidder] = auction.getRewardsFor(bidder, 0)
    expected_rewards[rewarded_bidder] = auction.getRewardsFor(
        rewarded_bidder, rewarded_bidder_holds
    )
    
    assert reward.balanceOf(auction) == 0

    assert expected_rewards[bidder] > 0
    assert expected_rewards[rewarded_bidder] > 0

    assert reward.balanceOf(bidder) == 0
    assert reward.balanceOf(rewarded_bidder) == 0

    assert reverts(lambda: auction.claimRewardTokensBasedOnShares(
        [0], 0, {'from': bidder}
    ))
    assert reverts(lambda: auction.claimRewardTokensBasedOnShares(
        rewarded_bidder_proof, rewarded_bidder_holds, {'from': rewarded_bidder}
    ))

    assert reward.balanceOf(bidder) == 0
    assert reward.balanceOf(rewarded_bidder) == 0

    assert expected_rewards[bidder] == auction.getRewardsFor(bidder, 0)
    assert expected_rewards[rewarded_bidder] == auction.getRewardsFor(
        rewarded_bidder, rewarded_bidder_holds
    )

def test_reward_claim():
    nft, reward, auction = deploy_weighted_rewarded_auction(
        reserve_price = 0.1,
        bid_increment = 0.05,
        root=root
    )
    
    initia_bal = toWei(100)

    reward.transfer(auction, initia_bal, {'from': accounts[0]})
    
    addr_to_helds = addr_to_derivs_held()

    rewarded_bidder = addr_to_helds[1][0]
    rewarded_bidder_proof = proofs[1]
    rewarded_bidder_holds = addr_to_helds[1][1]

    bidder = accounts[1]

    auction.createBid(1, {'from': bidder, 'value': toWei(0.1)})
    auction.createBid(1, {'from': rewarded_bidder, 'value': toWei(0.25)})
    auction.createBid(1, {'from': bidder, 'value': toWei(0.3)})

    rewards = {}
    rewards[bidder] = auction.getRewardsFor(bidder, 0)
    rewards[rewarded_bidder] = auction.getRewardsFor(
        rewarded_bidder, rewarded_bidder_holds
    )

    assert reward.balanceOf(auction) == initia_bal
    assert reward.balanceOf(bidder) == 0
    assert reward.balanceOf(rewarded_bidder) == 0

    auction.claimRewardTokensBasedOnShares(
        [0], 0, {'from': bidder}
    )

    assert reward.balanceOf(bidder) > 0 
    assert reward.balanceOf(auction) < initia_bal
    assert reward.balanceOf(bidder) == rewards[bidder]
    assert reward.balanceOf(auction) == initia_bal - rewards[bidder]

    auction.claimRewardTokensBasedOnShares(
        rewarded_bidder_proof, rewarded_bidder_holds, {'from': rewarded_bidder}
    )

    assert reward.balanceOf(rewarded_bidder) > 0
    assert reward.balanceOf(bidder) == rewards[bidder]
    assert reward.balanceOf(rewarded_bidder) == rewards[rewarded_bidder]
    assert (
        reward.balanceOf(auction) == 
        initia_bal - rewards[bidder] - rewards[rewarded_bidder]
    )

def test_access():
    nft, reward, auction = deploy_weighted_rewarded_auction(
        reserve_price = 0.1,
        bid_increment = 0.05,
        root=root
    )
    hacker = accounts[1]
    admin = accounts[0]
    bidder = accounts[2]

    reward.transfer(auction, toWei(100), {'from': admin})
    auction.createBid(1, {'from': bidder, 'value': toWei(0.1)})

    attacks = [
        lambda: auction.configureRewards(ZERO, (0,0), (0,0), 0, {'from': hacker}),
        lambda: auction.createBid(1, {'from': hacker, 'value': toWei(0.1499)}),
        lambda: auction.withdrawRewardToken({'from': hacker}),
        lambda: auction.setTimeBuffer(1, {'from': hacker}),
        lambda: auction.setDuration(1, {'from': hacker}),
        lambda: auction.settleAuction({'from': hacker})
    ]

    assert all(b for b in map(reverts, attacks))
    
    admin_manipulations = [
        lambda: auction.withdrawRewardToken({'from': admin}),
        lambda: auction.configureRewards(ZERO, (0,0), (0,0), 0, {'from': admin}),
        lambda: auction.setTimeBuffer(100, {'from': admin}),
        lambda: auction.setDuration(100, {'from': admin})
    ]

    assert all(not b for b in map(reverts, admin_manipulations))

    admin_wrong_manipulations = [
        lambda: auction.createBid(1, {'from': admin, 'value': toWei(0.1499)}),
        lambda: auction.setDuration(0, {'from': admin})
    ]

    assert all(b for b in map(reverts, admin_wrong_manipulations))


@pytest.mark.skip
def test_reward_claims():
    assert False

@pytest.mark.skip
def test_multiple_rewards_across_multiple_auctions():
    assert False

@pytest.mark.skip
def test_whitebox_reward_logic():
    assert False
