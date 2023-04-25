import brownie
from brownie import accounts, chain
from web3 import Web3
from itertools import starmap as nmap
from time import sleep
import pytest

from scripts.playground import (
    reverts,
    toWei,
    getparam
)

from scripts.deploy_helpers import deploy_rewarded_auction

def test_right_parameters():
    expected_max_supply = 312
    nft, reward, auction = deploy_rewarded_auction(max_supply = expected_max_supply)
    assert getparam("maxSupply", auction) == expected_max_supply
    assert getparam("nftContract", auction) == nft.address
    assert auction.rewardToken() == reward.address
 
def test_bid_ids():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(reserve_price=0.01, bid_increment=0.01)

    ids = [0, 1, 2, getparam('maxSupply', auction)+1, 12312312312, 1]
    prices = list(map(toWei, [0.1]*2 + [0.2]*4))
    assert len(ids) == len(prices)
    
    mkbid = lambda x, y: lambda: auction.createBid(x, {'value': y, 'from': bidder})

    assert reverts(mkbid(ids[0], prices[0]))
    assert not reverts(mkbid(ids[1], prices[1]))
    assert reverts(mkbid(ids[2], prices[2]))
    assert reverts(mkbid(ids[3], prices[3]))
    assert reverts(mkbid(ids[4], prices[4]))
    assert not reverts(mkbid(ids[5], prices[5]))
    
def test_bid_increment():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(reserve_price=0.01, bid_increment=0.01)
    prices = map(toWei, [0.01*i for i in range(1, 10)])
    prices2 = map(lambda x: x-1, prices)
    
    mkbid = lambda x: lambda: auction.createBid(1, {'value': x, 'from': bidder})
    bids = map(mkbid, prices)
    bids2 = map(mkbid, prices2)

    for x, y in zip(prices, prices2):
        assert not reverts(mkbid(x))
        assert reverts(mkbid(y))

def test_balances_for_one_bidder():
    bidder = accounts[1]
    initial_bal = bidder.balance()
    nft, reward, auction = deploy_rewarded_auction(reserve_price=0.01, bid_increment=0.01)

    prices = list(map(toWei, [0.01*i for i in range(1, 10)]))
    list(map(lambda x: auction.createBid(1, {'value': x, 'from': bidder}), prices))

    assert bidder.balance() == initial_bal - prices[-1]

def test_bid_parameters():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(
        reserve_price=0.01, auction_duration=5, extra_bid_time=3
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})

    assert getparam("bidder", auction) == bidder
    assert getparam("amount", auction) == toWei(0.01)
    assert getparam("nftId", auction) == 1
    assert not getparam("settled", auction)
    assert getparam("startTime", auction) > 0
    assert getparam("endTime", auction) > getparam("startTime", auction)

def test_auction_ending():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(
        reserve_price=0.01, auction_duration=3, extra_bid_time=2
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})
    sleep(5)
    chain.mine(1)

    assert auction.hasEnded()

def test_auction_settling():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(
        reserve_price=0.01, auction_duration=3, extra_bid_time=2
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})

    assert nft.balanceOf(bidder) == 0
    assert nft.balanceOf(auction.address) == 1

    sleep(5)
    chain.mine(1)
    
    auction.settleAuction({'from': bidder})
    assert nft.balanceOf(bidder) == 1
    assert nft.balanceOf(auction.address) == 0

def test_auction_new_bid_initialization():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(
        reserve_price=0.01, auction_duration=3, extra_bid_time=2
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})

    sleep(5)
    chain.mine(1)
   
    new_bidder = accounts[2]
    auction.createBid(2, {'value': toWei(0.01), 'from': new_bidder})

    assert nft.balanceOf(bidder) == 1
    assert nft.balanceOf(auction) == 1
    assert nft.balanceOf(new_bidder) == 0
    assert auction.balance() == toWei(0.01)*2

def test_withdraw_eth():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(
        reserve_price=0.01, auction_duration=3, extra_bid_time=2
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})

    sleep(5)
    chain.mine(1)

    initial_bal = accounts[0].balance()
    
    new_bidder = accounts[2]
    auction.createBid(2, {'value': toWei(0.01), 'from': new_bidder})
    auction.withdrawETH({'from': accounts[0]})
    
    assert auction.balance() == toWei(0.01)
    assert accounts[0].balance() > initial_bal + toWei(0.009)

def test_total_withdraw_after_total_supply():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(
        max_supply=1, 
        reserve_price=0.01,
        auction_duration=3,
        extra_bid_time=2
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})

    sleep(5)
    chain.mine(1)
    
    initial_bal = accounts[0].balance()
    assert auction.balance() == toWei(0.01)

    auction.withdrawETH({'from': accounts[0]})
    
    assert auction.balance() == 0
    assert accounts[0].balance() > initial_bal

def test_cant_bid_after_total_supply():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(
        max_supply=1, 
        reserve_price=0.01,
        auction_duration=3,
        extra_bid_time=2
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})

    sleep(5)
    chain.mine(1)

    new_bidder = accounts[2]
    assert not reverts(
        lambda: auction.createBid(2, {'value': toWei(0.01), 'from': new_bidder})
    )
    assert new_bidder.balance() > new_bidder.balance() - toWei(0.01)
    assert auction.balance() == toWei(0.01)

    chain.mine(1)

    assert nft.balanceOf(auction) == 0
    assert nft.balanceOf(new_bidder) == 0
    assert nft.balanceOf(bidder) == 1

    assert reverts(
        lambda: auction.settleAuction({'from': new_bidder})
    )

    assert nft.balanceOf(auction) == 0
    assert nft.balanceOf(new_bidder) == 0
    assert nft.balanceOf(bidder) == 1

def test_multiple_biddings_and_mintings():
    assert False

def test_bid_reward_shares():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(
        reserve_price=0.01, bid_increment = 0.005
    )

    auction.createBid(1, {'from': bidder, 'value': toWei(0.01)})
    assert auction.rewardTokenShares(bidder) == toWei(0.01)

    auction.claimRewardTokensBasedOnShares({'from': bidder})
    assert auction.rewardTokenShares(bidder) == 0

    auction.claimRewardTokensBasedOnShares({'from': bidder})
    assert auction.rewardTokenShares(bidder) == 0

    auction.createBid(1, {'from': bidder, 'value': toWei(0.025)})
    assert auction.rewardTokenShares(bidder) == toWei(0.025)

    auction.claimRewardTokensBasedOnShares({'from': bidder})
    assert auction.rewardTokenShares(bidder) == 0


def test_bid_reward_claims():
    bidder = accounts[1]
    nft, reward, auction = deploy_rewarded_auction(
        reserve_price=0.01, bid_increment = 0.005
    )

    ratio = reward.getRewardRatio()

    auction.createBid(1, {'from': bidder, 'value': toWei(0.01)})
    assert reward.balanceOf(bidder) == 0

    auction.claimRewardTokensBasedOnShares({'from': bidder})
    assert reward.balanceOf(bidder) == toWei(0.01) * ratio

    auction.claimRewardTokensBasedOnShares({'from': bidder})
    assert reward.balanceOf(bidder) == toWei(0.01) * ratio

    auction.createBid(1, {'from': bidder, 'value': toWei(0.025)})
    assert reward.balanceOf(bidder) == toWei(0.01) * ratio

    auction.claimRewardTokensBasedOnShares({'from': bidder})
    assert reward.balanceOf(bidder) == toWei(0.035) * ratio

def test_inherited_onlyowner():
    nft, reward, auction = deploy_rewarded_auction()
    assert reverts(lambda:
        auction.setRewardTokenAddress(accounts[1], {'from': accounts[1]})
    )

