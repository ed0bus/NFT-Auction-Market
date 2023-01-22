from djongo import models
from djongo.models import ObjectIdField

# Create your models here.
class AuctionObject(models.Model):
    _id = models.ObjectIdField()
    minted_by = models.CharField(max_length=42)
    nft_id = models.IntegerField()
    token_uri = models.CharField(max_length=100)
    tx_hash = models.CharField(max_length=50)


class RefundedMoney(models.Model):
    _id = models.ObjectIdField()
    refunded_address = models.CharField(max_length=42)
    amount = models.FloatField()
    tx_hash = models.CharField(max_length=50)


class AuctionCreation(models.Model):
    _id = models.ObjectIdField()
    seller = models.CharField(max_length=42)
    auction_id = models.IntegerField()
    nft_id = models.IntegerField()
    endtime = models.DateTimeField()
    minimum_bid = models.FloatField()
    tx_hash = models.CharField(max_length=50)


class PlacedBid(models.Model):
    _id = models.ObjectIdField()
    bidder = models.CharField(max_length=42)
    auction_id = models.IntegerField()
    amount = models.FloatField()
    tx_hash = models.CharField(max_length=50)


class EndedAuction(models.Model):
    _id = models.ObjectIdField()
    auction_id = models.IntegerField()
    winner_offer = models.FloatField()
    winner_address = models.CharField(max_length=42)
    tx_hash = models.CharField(max_length=50)


class NotFinalizedWithdraw(models.Model):
    _id = models.ObjectIdField()
    auction_id = models.IntegerField()
    amount = models.FloatField()
    recipient = models.CharField(max_length=42)
    tx_hash = models.CharField(max_length=50)
