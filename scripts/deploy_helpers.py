import brownie
from brownie import (
    MinimalAuctionableToken,
    RewardedAuction,
    AuctionRewardToken
)
from brownie import accounts
from scripts.playground import toWei

def deploy_rewarded_auction(
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

    auction_house = RewardedAuction.deploy({'from': acc})
    auction_house.initialize(
        nft.address,
        max_supply,
        toWei(reserve_price),
        toWei(bid_increment),
        auction_duration,
        extra_bid_time,
        {'from': acc}
    )
    auction_house.setRewardTokenAddress(reward.address, {'from': acc})

    nft.setMinter(auction_house.address, {'from': acc})
    reward.setMinter(auction_house.address, {'from': acc})
    
    return nft, reward, auction_house

