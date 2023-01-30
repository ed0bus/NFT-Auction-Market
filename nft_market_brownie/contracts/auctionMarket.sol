// SPDX-License-Identifier: MIT-3.0
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

//This contract let you mint your NFT and make it possible to auction it
contract NFTAuctionMarket is ERC721URIStorage {
    mapping(uint256 => Auction) public auctions; //map auction id to auction status
    uint256 public auctionID; //if AuctionID > 1: created_auctions = AuctionID -1
    uint256 public tokenCounter; //track NFT counter
    mapping(address => uint256) public biddersToOverbiddenBids;
    mapping(uint256 => bool) public onAuctionNFTs;//track nft being auctioned

    //define events
    event auctionObjectCreation(address _from, uint256 _nftId, string _tokenURI); 
    event moneyRefunded(address _to, uint256 _amount);
    event auctionEvent(address _from, uint256 _auctionID, uint256 _nftId, uint256 _endTime, uint256 _minimumBid);
    event bidPlaced(address _from, uint256 _auctionID, uint256 _amount);
    event finalizedAuction(
        uint256 _auctionID,
        uint256 _highestBid,
        address _auctionWinner
    );
    event withdrawNotFinalizedAuction(uint256 _auctionId, address _from, uint256 _amount);

    constructor() ERC721("AuctionObject", "AO") {
        tokenCounter = 0;
        auctionID = 0;
    }

    
    struct Auction {
        uint256 nftId; 
        address seller;
        address highestBidder;
        uint256 highestBid;
        uint256 endTime;
        uint256 minimumBid;
        bool ended;
        bool started;
    }

    //function to mint nft AO
    function createAuctionObject(string memory tokenURI) public returns (uint256) {
        uint256 objectID = tokenCounter; //nft token counter
        _safeMint(msg.sender, objectID); //nft minting
        _setTokenURI(objectID, tokenURI);
        tokenCounter = tokenCounter + 1;
        emit auctionObjectCreation(msg.sender, objectID, tokenURI);
        return objectID;
    }

    //let users withdraw overbidden sums
    function withdrawOverbidden() external {
        uint256 amount = biddersToOverbiddenBids[msg.sender];
        require(amount > 0, "You have no overbidden amount to withdraw!");
        biddersToOverbiddenBids[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
        emit moneyRefunded(msg.sender, amount);
    }

    // Start a new auction for an NFT
    function startAuction(uint256 _nftId, uint256 _endtime, uint256 _minimumBid) public {
        //conditions
        require(
            ownerOf(_nftId) == msg.sender,
            "You are not the owner of the NFT"
        );
        
        // Check if the NFT is already being auctioned
        require(onAuctionNFTs[_nftId] == false, "The Nft is already being auctioned");

            
        // Create a new auction
        auctions[auctionID] = Auction(
            _nftId,
            msg.sender, // Seller address
            address(0), // No highest bidder yet
            0, // No bids yet
            block.timestamp + _endtime, // Auction end time
            _minimumBid, 
            false, // Auction has not ended yet
            true // Auction has started
        );
        onAuctionNFTs[_nftId] = true; //selected nft is now being auctioned
        auctionID = auctionID + 1;
        emit auctionEvent(msg.sender, auctionID, _nftId, block.timestamp + _endtime, _minimumBid);
    }

    // Place a bid on an NFT auction
    function bid(uint256 _auctionID) public payable {
        // Get the correspondent auction
        Auction storage auction = auctions[_auctionID];
        //Check conditions
        require(auction.started, "Auction has not started yet!");
        require(
            auction.seller != msg.sender,
            "You can't bid on your own auction!"
        );
        require(!auction.ended, "Auction has already ended");
        //Check time
        require(
            block.timestamp <= auction.endTime,
            "Auction time has expired! This auction is pending for finalization!"
        );
        // Check if the bid is higher than the current highest bid
        require(
            msg.value > auction.highestBid,
            "Bid is not higher than current highest bid"
        );
        require( msg.value > auction.minimumBid, "Your bid should be higher than the minimum Bid");
        //track overbiddenbids
        if (auction.highestBid != 0) {
            biddersToOverbiddenBids[auction.highestBidder] += auction
                .highestBid;
        }

        // Update the auction with the new highest bid
        auction.highestBidder = msg.sender;
        auction.highestBid = msg.value;
        emit bidPlaced(msg.sender, _auctionID, msg.value);
    }

    

    // End an auction and transfer the NFT to the highest bidder
    //only the nft seller/owner should be able to call this function
    function endAuction(uint256 _auctionID) public {
        // Get the current auction
        Auction storage auction = auctions[_auctionID];
        //conditions
        // Check if the auction is still active
        require(!auction.ended, "Auction has already ended");
        require(msg.sender == auction.seller, "Sender is not the seller");
        require(
            block.timestamp >= auction.endTime,
            "Auction has not ended yet"
        );
        // Mark the auction as ended
        auction.ended = true;
        // If there is a highest bidder, transfer their bid to the seller
        if (auction.highestBidder != address(0)) {
            payable(auction.seller).transfer(auction.highestBid);
            // Transfer the NFT to the highest bidder
            safeTransferFrom(msg.sender, auction.highestBidder, auction.nftId);
            
        }

        //object can be ipotetically be reauctioned. the important thing is to remove objects from on auctionNFT
        onAuctionNFTs[auction.nftId] = false;
        
        emit finalizedAuction(
            _auctionID,
            auction.highestBid,
            auction.highestBidder
        );
    }
     
    //highestBidder can withdraw the highest bid amount back if auctioneer doesnt finalized it within 24 hours
    function withdrawNotFinalized(uint256 _auctionID) external {
        Auction storage auction = auctions[_auctionID];
        require(block.timestamp >= auction.endTime, "Auction has not ended yet");
        require(msg.sender == auction.highestBidder, "You are not the auction winner!");
        require(block.timestamp >= (auction.endTime + 86400), "24 hours have not passed yet");
        require(!auction.ended, "This auction has been already finalized, there's no amount to withdraw");
        payable(msg.sender).transfer(auction.highestBid);
        uint256 amount = auction.highestBid;
        auction.highestBid = 0;
        auction.highestBidder = 0x0000000000000000000000000000000000000000;
        auction.ended = true;
        emit withdrawNotFinalizedAuction(_auctionID, msg.sender, amount);
        
    }

}