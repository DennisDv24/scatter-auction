import brownie
from brownie import (
    MinimalAuctionableToken,
    ScatterAuction,
    AuctionRewardToken
)
from brownie import accounts
from web3 import Web3
from itertools import starmap as nmap
from time import sleep
import pytest

toWei = lambda x: Web3.toWei(x, 'ether')

def reverts(f):
    try:
        with brownie.reverts():
            f()
    except:
        return False
    return True

def deploy_system(
    max_supply = 10000,
    reserve_price = 0.1,
    bid_increment = 0.05,
    auction_duration = 60 * 60 * 3,
    extra_bid_time = 60 * 5
):
    acc = accounts[0]
    nft = MinimalAuctionableToken.deploy(
        "DeploymentTest",
        "DT",
        {'from': acc}
    )
    reward = AuctionRewardToken.deploy(
        "RewardToken",
        "RT",
        {'from': acc}
    )

    auction_house = ScatterAuction.deploy({'from': acc})
    auction_house.initialize(
        nft.address,
        max_supply,
        toWei(reserve_price),
        toWei(bid_increment),
        auction_duration,
        extra_bid_time,
        reward.address,
        {'from': acc}
    )

    nft.setMinter(auction_house.address, {'from': acc})
    reward.setMinter(auction_house.address, {'from': acc})
    
    return nft, reward, auction_house

def test_trivial():
    nft, reward, auction_house = deploy_system()
    assert 1 == 1

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


def test_right_parameters():
    expected_max_supply = 312
    nft, reward, auction = deploy_system(max_supply = expected_max_supply)
    assert getparam("maxSupply", auction) == expected_max_supply
    assert getparam("nftContract", auction) == nft.address
    assert getparam("rewardToken", auction) == reward.address
 
def test_bid_ids():
    bidder = accounts[1]
    nft, reward, auction = deploy_system(reserve_price=0.01, bid_increment=0.01)

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
    nft, reward, auction = deploy_system(reserve_price=0.01, bid_increment=0.01)
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
    nft, reward, auction = deploy_system(reserve_price=0.01, bid_increment=0.01)

    prices = list(map(toWei, [0.01*i for i in range(1, 10)]))
    list(map(lambda x: auction.createBid(1, {'value': x, 'from': bidder}), prices))

    assert bidder.balance() == initial_bal - prices[-1]

def test_bid_parameters():
    bidder = accounts[1]
    nft, reward, auction = deploy_system(
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
    nft, reward, auction = deploy_system(
        reserve_price=0.01, auction_duration=5, extra_bid_time=3
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})
    sleep(15)

    assert auction.hasEnded()

@pytest.mark.skip
def test_auction_settling():
    bidder = accounts[1]
    nft, reward, auction = deploy_system(
        reserve_price=0.01, auction_duration=5, extra_bid_time=3
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})
    sleep(15)

    new_bidder = accounts[2]
    auction.createBid(2, {'value': toWei(0.01), 'from': new_bidder})
    assert nft.balanceOf(bidder) == 1


