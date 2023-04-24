import brownie
from brownie import (
    MinimalAuctionableToken,
    ScatterAuction,
    AuctionRewardToken
)
from brownie import accounts
from web3 import Web3

def deploy_system(
    max_supply,
    reserve_price,
    bid_increment,
    auction_duration,
    extra_bid_time
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
        Web3.toWei(reserve_price, 'ether'),
        Web3.toWei(bid_increment, 'ether'),
        auction_duration,
        extra_bid_time,
        reward.address,
        {'from': acc}
    )

    nft.setMinter(auction_house.address, {'from': acc})
    reward.setMinter(auction_house.address, {'from': acc})
    
    return nft, reward, auction_house

def deploy_fast_system():
    nft, reward, auction_house = deploy_system(
        100,
        0.1,
        0.05,
        20, # 20 seconds per auction
        5 # 5 extra seconds per last bid
    )
    return nft, reward, auction_house

def main():
    nft, reward, auction_house = deploy_fast_system()
    print(auction_house.auctionData())
    

