from scripts.deploy_helpers import deploy_scatter_auction
from time import sleep
from brownie import chain, accounts
from scripts.playground import toWei
from scripts.playground import getparam

PLATFORM = '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'

def test_withdraws():
    nft, reward, auction = deploy_scatter_auction(
        reserve_price=0.1,
        auction_duration=5,
        extra_bid_time=3,
        bid_increment=0.05
    )
    
    auction.createBid(1, {'from': accounts[1], 'value': toWei(0.1)})
    auction.createBid(1, {'from': accounts[2], 'value': toWei(0.15)})
    auction.createBid(1, {'from': accounts[1], 'value': toWei(0.3)})
    
    sleep(5)
    chain.mine(1)

    auction.createBid(2, {'from': accounts[3], 'value': toWei(0.1)})
    sleep(3)
    auction.createBid(2, {'from': accounts[2], 'value': toWei(0.15)})
    sleep(1)
    auction.createBid(2, {'from': accounts[3], 'value': toWei(0.3)})
    sleep(1)
    auction.createBid(2, {'from': accounts[2], 'value': toWei(0.4)})
    sleep(1)
    auction.createBid(2, {'from': accounts[4], 'value': toWei(0.5)})
    sleep(3)

    chain.mine(1)

    auction.settleAuction({'from': accounts[5]})

    assert nft.balance() == toWei(0.3) + toWei(0.5)
        
    plat = accounts.at(PLATFORM, force=True)
    initial_platform_bal = plat.balance()
    initial_owner_bal = accounts[0].balance()

    tx = nft.withdraw({'from': accounts[5]})

    assert accounts[0].balance() == initial_owner_bal + toWei(0.76)
    assert plat.balance() == initial_platform_bal + toWei(0.04)


