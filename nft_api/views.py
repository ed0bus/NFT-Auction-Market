from django.shortcuts import render
import json as json
from web3 import Web3
from django.http import JsonResponse, HttpResponse
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from django.forms.models import model_to_dict

# Create your views here.
from .models import (
    AuctionCreation,
    AuctionObject,
    RefundedMoney,
    PlacedBid,
    EndedAuction,
    NotFinalizedWithdraw,
)

# connect to eth node
alchemy_url = "INSERT ALCHEMY ENDPOINT"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

with open(
    "INSERT YOUR CONTRACT.json HERE"  # look into the build folder of the nft_market_brownie. Notice you'll have to compile and deploy the contract first.
) as f:
    auction_contract = json.load(f)
    abi = auction_contract["abi"]
    address = w3.toChecksumAddress("INSERT THE DEPLOYED CONTRACT ADDRESS")

contract = w3.eth.contract(
    address=address,
    abi=abi,
)

#


# nft event creation json
def nft_creation_api(request):
    auction_event_filter = contract.events.auctionObjectCreation.createFilter(
        fromBlock=0
    )
    # get all events
    ao_events = auction_event_filter.get_all_entries()
    # save args events in a list of dictionaries
    args_dict_list = [dict(event["args"]) for event in ao_events]
    # create a list of properly formatted transaction hashes
    tx_hashes = [event["transactionHash"].hex() for event in ao_events]
    # and associate every args dictionary to its proper tx_hash key-value pair base on index order
    for i, d in enumerate(args_dict_list):
        d["tx_hash"] = tx_hashes[i]

    api = {"nft_mints": args_dict_list}
    for x in api["nft_mints"]:
        # do nothing if a record of the event is already stored in mongo db
        if AuctionObject.objects.filter(tx_hash=x["tx_hash"]):
            pass
        # else create a new event and store it
        else:
            AuctionObject.objects.create(
                minted_by=x["_from"],
                nft_id=x["_nftId"],
                token_uri=x["_tokenURI"],
                tx_hash=x["tx_hash"],
            )
    query_set = AuctionObject.objects.all()
    parsed_data = json.loads(serialize("json", query_set))
    return JsonResponse(api, safe=False)


def overbidden_bids_api(request):
    auction_event_filter = contract.events.moneyRefunded.createFilter(fromBlock=0)
    ob_events = auction_event_filter.get_all_entries()
    args_dict_list = [dict(event["args"]) for event in ob_events]
    tx_hashes = [event["transactionHash"].hex() for event in ob_events]
    for i, d in enumerate(args_dict_list):
        d["tx_hash"] = tx_hashes[i]

    api = {"overbidden_bids": args_dict_list}
    for x in api["overbidden_bids"]:
        if RefundedMoney.objects.filter(tx_hash=x["tx_hash"]):
            pass
        else:
            RefundedMoney.objects.create(
                refunded_address=x["_to"],
                amount=w3.fromWei(x["_amount"], "ether"),
                tx_hash=x["tx_hash"],
            )

    return JsonResponse(api)


# nft event creation json
def auction_creation_api(request):
    auction_event_filter = contract.events.auctionEvent.createFilter(fromBlock=0)
    ao_events = auction_event_filter.get_all_entries()
    args_dict_list = [dict(event["args"]) for event in ao_events]

    tx_hashes = [event["transactionHash"].hex() for event in ao_events]

    for i, d in enumerate(args_dict_list):
        d["tx_hash"] = tx_hashes[i]
    api = {"auctions": args_dict_list}
    for x in api["auctions"]:
        if AuctionCreation.objects.filter(tx_hash=x["tx_hash"]):
            pass
        else:
            AuctionCreation.objects.create(
                seller=x["_from"],
                auction_id=x["_auctionID"],
                nft_id=x["_nftId"],
                endtime=datetime.datetime.fromtimestamp(x["_endTime"]),
                minimum_bid=w3.fromWei(x["_minimumBid"], "ether"),
                tx_hash=x["tx_hash"],
            )

    return JsonResponse(api)


def bid_events_api(request):
    auction_event_filter = contract.events.bidPlaced.createFilter(fromBlock=0)
    ob_events = auction_event_filter.get_all_entries()
    args_dict_list = [dict(event["args"]) for event in ob_events]
    tx_hashes = [event["transactionHash"].hex() for event in ob_events]
    for i, d in enumerate(args_dict_list):
        d["tx_hash"] = tx_hashes[i]
    api = {"bids": args_dict_list}
    for x in api["bids"]:
        if PlacedBid.objects.filter(tx_hash=x["tx_hash"]):
            pass
        else:
            PlacedBid.objects.create(
                bidder=x["_from"],
                auction_id=x["_auctionID"],
                amount=w3.fromWei(x["_amount"], "ether"),
                tx_hash=x["tx_hash"],
            )

    return JsonResponse(api, safe=False)


def auction_finalized_api(request):
    auction_event_filter = contract.events.finalizedAuction.createFilter(fromBlock=0)
    af_events = auction_event_filter.get_all_entries()
    args_dict_list = [dict(event["args"]) for event in af_events]
    tx_hashes = [event["transactionHash"].hex() for event in af_events]
    for i, d in enumerate(args_dict_list):
        d["tx_hash"] = tx_hashes[i]
    api = {"finalized_auctions": args_dict_list}
    for x in api["finalized_auctions"]:
        if EndedAuction.objects.filter(tx_hash=x["tx_hash"]):
            pass
        else:
            EndedAuction.objects.create(
                auction_id=x["_auctionID"],
                winner_offer=w3.fromWei(x["_highestBid"], "ether"),
                winner_address=x["_auctionWinner"],
                tx_hash=x["tx_hash"],
            )
    return JsonResponse(api)


def not_finalized_auction_api(request):
    auction_event_filter = contract.events.withdrawNotFinalizedAuction.createFilter(
        fromBlock=0
    )
    nfa_events = auction_event_filter.get_all_entries()
    args_dict_list = [dict(event["args"] for event in nfa_events)]
    tx_hashes = [event["transactionHash"].hex() for event in nfa_events]
    for i, d in enumerate(args_dict_list):
        d["tx_hash"] = tx_hashes[i]
    api = {"not_finalized_auctions": args_dict_list}
    for x in api["not_finalized_auctions"]:
        if NotFinalizedWithdraw.objects.filter(tx_hash=x["tx_hash"]):
            pass
        else:
            NotFinalizedWithdraw.objects.create(
                auction_id=x["_auctionId"],
                amount=w3.fromWei(x["_amount"], "ether"),
                recipient=x["_from"],
                tx_hash=x["tx_hash"],
            )

    return JsonResponse(api)
