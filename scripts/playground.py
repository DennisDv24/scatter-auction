import brownie
from brownie import (
    MinimalAuctionableToken,
    ScatterAuction,
    AuctionRewardToken
)
from brownie import accounts
from web3 import Web3

toWei = lambda x: Web3.toWei(x, 'ether')

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

def main():
    bidder = accounts[1]
    nft, reward, auction = deploy_system(
        reserve_price=0.01, auction_duration=5, extra_bid_time=3
    )
    auction.createBid(1, {'value': toWei(0.01), 'from': bidder})
    sleep(15)

    print(auction.hasEnded())
    

