from brownie import NFTAuctionMarket
from scripts.helpful_scripts import get_account, accounts, config
import time
from brownie.network.state import Chain
from scripts.pinata import (
    load_file_to_ipfs,
    load_json_to_ipfs,
    erc721_metadata_json_schema,
)
from datetime import timedelta
from brownie import Wei
import datetime

chain = Chain()

#you can insert a contract directly deployed by you, this is just a sample of an already deployed contract

contract = "INSERT CONTRACT ADDRESS HERE"
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-prova"]


def deploy_contract():
    account = get_account(0)
    nft_auction_market = NFTAuctionMarket.deploy({"from": account})
    print("contract deployed")


def mint_nft():
    account = get_account(0)
    nft_auction_market = NFTAuctionMarket.at(contract)
    image = load_file_to_ipfs()
    data = erc721_metadata_json_schema(image_uri=image)
    nft_uri = load_json_to_ipfs(data)
    tx = nft_auction_market.createAuctionObject(nft_uri, {"from": account})


# tomorrow add auctionID as an input parameter
def bid_on_auction(auctionID):
    account = get_account(4)
    nft_auction_market = NFTAuctionMarket.at(contract)
    amount = input(
        'How many ether? (You have to specify quantity and unit, ex "1 ether" '
    )
    quantity = Wei(amount)
    bidding = nft_auction_market.bid(auctionID, {"from": account, "value": quantity})
    print(f"You are bidding on the auction n. {auctionID}")
    print("Funding...")
    print("Funding completed!")


def start_auction():
    account = get_account(2)
    nft_auction_market = NFTAuctionMarket.at(contract)
    nft_id = int(input("Digit the Id of the nft you want to auction:"))
    hours = int(input("How many hours do you want your auction to last?"))
    minutes = int(input("And How many minutes?"))
    duration = timedelta(hours=hours, minutes=minutes).total_seconds()
    minimum_bid = input(
        'How many ether? (You have to specify quantity and unit, ex "1 ether" '
    )
    minimum_bid_to_eth = Wei(minimum_bid)
    start = nft_auction_market.startAuction(
        nft_id, duration, minimum_bid_to_eth, {"from": account}
    )


def withdraw_overbidden():
    account = get_account(1)
    nft_auction_market = NFTAuctionMarket.at(contract)
    nft_auction_market.withdrawOverbidden({"from": account})
    print("You have succesfully withdrawn your overbidden bids!!")


# call function
def auctions_info():
    auction_index = int(input("Which auction do you want info on? "))
    account = get_account(0)
    nft_auction_market = NFTAuctionMarket.at(contract)
    nft_id = nft_auction_market.auctions(auction_index)["nftId"]
    seller = nft_auction_market.auctions(auction_index)["seller"]
    highest_bidder = nft_auction_market.auctions(auction_index)["highestBidder"]
    highest_bid = (
        str(Wei(nft_auction_market.auctions(auction_index)["highestBid"]).to("ether"))
        + " ETH"
    )

    end_time = nft_auction_market.auctions(auction_index)["endTime"]
    minimum_bid = (
        str(Wei(nft_auction_market.auctions(auction_index)["minimumBid"]).to("ether"))
        + " ETH"
    )

    ended = nft_auction_market.auctions(auction_index)["ended"]
    started = nft_auction_market.auctions(auction_index)["started"]
    orario = datetime.datetime.fromtimestamp(end_time)
    print(f"The nft id of the auction is {nft_id}")
    print(f"The auction will end at: {orario}")
    print(f"The auction seller is: {seller}")
    print(f"The auction highestBidder is: {highest_bidder}")
    print(f"The auction highest bid is: {highest_bid}")
    print(f"The minimum bid is: {minimum_bid}")
    print(f"Has the auction ended? {ended}")
    print(f"Has the auction started? {started}")


def endAuction():
    account = get_account(0)
    auction_id = int(input("Digit the ID of the auction you want to finalize:"))
    nft_auction_market = NFTAuctionMarket.at(contract)
    chain.sleep(900000)  # va tolto
    chain.mine()
    nft_auction_market.endAuction(auction_id, {"from": account})
    print("Auction succesfully ended!")


def withdraw_not_finalized():
    account = get_account(4)
    auction_id = int(input("Digit the ID of the auction you want to finalize:"))
    nft_auction_market = NFTAuctionMarket.at(contract)
    chain.sleep(900000)  # va tolto
    chain.mine()
    nft_auction_market.withdrawNotFinalized(auction_id, {"from": account})
    print(
        "You have succesfully withdraw your offer since the auctioner has not finalized the auction withing 24 hours!!"
    )


def main():
    mint_nft()
