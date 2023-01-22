from brownie import NFTAuctionMarket
from scripts.helpful_scripts import get_account
from brownie import accounts
from brownie.network.state import Chain
from scripts.deploy import deploy_contract

chain = Chain()

# let's test our contract
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-prova"]


def test_deploy():
    # arrange
    account = get_account(0)
    # act
    nft_auction_market = NFTAuctionMarket.deploy({"from": account})
    token_counter = nft_auction_market.tokenCounter({"from": account})
    expected = 0
    # assert
    assert expected == token_counter


def test_create_nft():
    # arrange
    account = get_account(0)
    # act
    nft_auction_market = NFTAuctionMarket.deploy({"from": account})
    create_nft = nft_auction_market.createAuctionObject("uri_sample", {"from": account})
    create_nft.wait(1)
    expected_owner = account
    # assert
    assert expected_owner == nft_auction_market.ownerOf(
        nft_auction_market.tokenCounter() - 1
    )


def test_auction_creation():
    # arrange
    seller_account = get_account(0)
    bidder_account = get_account(2)
    nft_auction_market = NFTAuctionMarket.deploy({"from": seller_account})
    # act:
    # -create nft
    nft = nft_auction_market.createAuctionObject("uri_sample", {"from": seller_account})
    nft_id = (nft_auction_market.tokenCounter({"from": seller_account})) - 1
    # -create auction
    auction = nft_auction_market.startAuction(nft_id, 10, 100, {"from": seller_account})
    auctionID = nft_auction_market.auctionID() - 1
    auction_object = nft_auction_market.auctions(auctionID)
    # assert
    assert auction_object["seller"] == seller_account
    assert auction_object["minimumBid"] == 100
    assert auction_object["nftId"] == nft_id


def test_bid():
    # arrange
    bidder_account = get_account(4)
    seller_account = get_account(3)
    # act
    nft_auction_market = NFTAuctionMarket.deploy({"from": seller_account})
    nft = nft_auction_market.createAuctionObject("uri_sample", {"from": seller_account})
    nft_id = (nft_auction_market.tokenCounter({"from": seller_account})) - 1
    auction = nft_auction_market.startAuction(
        nft_id, 100, 100, {"from": seller_account}
    )
    auctionID = nft_auction_market.auctionID() - 1
    amount = 1e18
    nft_auction_market.bid(auctionID, {"from": bidder_account, "amount": amount})
    auction_object = nft_auction_market.auctions(auctionID)
    # assert
    assert auction_object["highestBidder"] == bidder_account
    assert auction_object["highestBid"] == amount


def test_end_auction():
    # arrange
    seller_account = get_account(1)
    bidder_account = get_account(2)
    initial_balance = seller_account.balance()
    # act
    nft_auction_market = NFTAuctionMarket.deploy({"from": get_account(3)})
    # create nft
    nft = nft_auction_market.createAuctionObject("uri_sample", {"from": seller_account})
    nft_id = (nft_auction_market.tokenCounter({"from": seller_account})) - 1
    # create auction
    auction = nft_auction_market.startAuction(nft_id, 20, 100, {"from": seller_account})
    auctionID = nft_auction_market.auctionID() - 1
    # bid on auction
    amount = 1e18
    nft_auction_market.bid(auctionID, {"from": bidder_account, "amount": amount})

    chain.sleep(1000)
    chain.mine()
    nft_auction_market.endAuction(auctionID, {"from": seller_account})
    updated = nft_auction_market.auctions(auctionID)
    updated_balance = get_account(1).balance()

    assert updated["ended"] == True
    assert seller_account.balance() == updated_balance


def test_withdraw_overbidden():
    # arrange
    seller_account = get_account(1)
    bidder_account = get_account(2)
    overbidder_account = get_account(3)
    nft_auction_market = NFTAuctionMarket.deploy({"from": get_account(1)})
    # create nft
    nft = nft_auction_market.createAuctionObject("uri_sample", {"from": seller_account})
    nft_id = (nft_auction_market.tokenCounter({"from": seller_account})) - 1
    # create auction
    auction = nft_auction_market.startAuction(nft_id, 20, 100, {"from": seller_account})
    auctionID = nft_auction_market.auctionID() - 1
    # bid on auction
    overbidden_amount = 1e18
    amount = 2e18
    nft_auction_market.bid(
        auctionID, {"from": overbidder_account, "amount": overbidden_amount}
    )
    nft_auction_market.bid(auctionID, {"from": bidder_account, "amount": amount})

    nft_auction_market.withdrawOverbidden({"from": overbidder_account})
    actual_balance = get_account(3).balance()
    # assert
    assert overbidder_account.balance() == actual_balance


def test_withdraw_not_finalized():
    # arrange
    seller_account = get_account(1)
    bidder_account = get_account(2)
    initial_balance = bidder_account.balance()
    nft_auction_market = NFTAuctionMarket.deploy({"from": get_account(1)})
    # create nft
    nft = nft_auction_market.createAuctionObject("uri_sample", {"from": seller_account})
    nft_id = (nft_auction_market.tokenCounter({"from": seller_account})) - 1
    # create auction
    auction = nft_auction_market.startAuction(nft_id, 20, 100, {"from": seller_account})
    auctionID = nft_auction_market.auctionID() - 1
    # bid on auction

    amount = 2e18
    nft_auction_market.bid(auctionID, {"from": bidder_account, "amount": amount})
    # fast forward the blockchain to test the function
    chain.sleep(900000)
    chain.mine()
    # withdraw not finalized offer
    nft_auction_market.withdrawNotFinalized(auctionID, {"from": bidder_account})
    auction_object = nft_auction_market.auctions(auctionID)
    # assert
    assert auction_object["highestBid"] == 0
    assert (
        auction_object["highestBidder"] == "0x0000000000000000000000000000000000000000"
    )
    assert auction_object["ended"] == True
