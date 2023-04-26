import brownie
from brownie import (
    MinimalAuctionableNFT,
    RewardedAuction,
    AuctionRewardToken,
    TestToken,
    ScatterAuction,
    WeightedRewardedAuction
)
from brownie import accounts
from scripts.playground import toWei


def deploy_simple_auction(
    max_supply = 10000,
    reserve_price = 0.1,
    bid_increment = 0.05,
    auction_duration = 60 * 60 * 3,
    extra_bid_time = 60 * 5,
    auction_contract = ScatterAuction
):
    nft = MinimalAuctionableNFT.deploy(
        "DeploymentTest",
        "DT",
        {'from': accounts[0]}
    )

    auction_house = auction_contract.deploy({'from': accounts[0]})
    auction_house.initialize(
        nft.address,
        max_supply,
        toWei(reserve_price),
        toWei(bid_increment),
        auction_duration,
        extra_bid_time,
        {'from': accounts[0]}
    )

    nft.setMinter(auction_house, {'from': accounts[0]})

    return nft, (), auction_house

def deploy_rewarded_auction(
    max_supply = 10000,
    reserve_price = 0.1,
    bid_increment = 0.05,
    auction_duration = 60 * 60 * 3,
    extra_bid_time = 60 * 5
):
    nft, _, auction = deploy_simple_auction(
        max_supply, 
        reserve_price,
        bid_increment,
        auction_duration,
        extra_bid_time,
        auction_contract = RewardedAuction
    )

    reward = AuctionRewardToken.deploy(
        "RewardToken",
        "RT",
        {'from': accounts[0]}
    )

    auction.setRewardTokenAddress(reward.address, {'from': accounts[0]})
    reward.setMinter(auction.address, {'from': accounts[0]})
    
    return nft, reward, auction

def deploy_weighted_rewarded_auction(
    max_supply = 10000,
    reserve_price = 0.1,
    bid_increment = 0.05,
    auction_duration = 60 * 60 * 3,
    extra_bid_time = 60 * 5,
    reward_ratio = (1, 1),
    extra_ratio = (1, 10),
    root = 0
):
    nft, _, auction = deploy_simple_auction(
        max_supply, 
        reserve_price,
        bid_increment,
        auction_duration,
        extra_bid_time,
        auction_contract = WeightedRewardedAuction
    )

    token = TestToken.deploy({'from': accounts[0]})
    
    auction.configureRewards(
        token.address,
        reward_ratio,
        extra_ratio,
        root
    )

    return nft, token, auction
