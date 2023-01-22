from django.urls import path
from . import views

urlpatterns = [
    path("nftcreation", views.nft_creation_api, name="nftcreation"),
    path("overbiddenbids", views.overbidden_bids_api, name="overbiddenbids"),
    path("auctioncreation", views.auction_creation_api, name="auctioncreation"),
    path("bid_events", views.bid_events_api, name="bid"),
    path("finalized_auctions", views.auction_finalized_api, name="finalizedauction"),
]
