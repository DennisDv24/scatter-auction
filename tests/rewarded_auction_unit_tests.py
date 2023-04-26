from brownie import accounts, chain
from web3 import Web3
import pytest

from scripts.playground import (
    reverts,
    toWei,
    getparam
)

from scripts.deploy_helpers import deploy_rewarded_auction


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

