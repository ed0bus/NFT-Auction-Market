## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
The scope of the project is to create a smart contract auction market that lets the users auction any asset in the same way of a physical auction.
The user can interact with or deploy the contract using Remix or locally. To interact with it directly from your terminal follow the instructions below.
Contract functions are the following:

* Mint an NFT Auction Object (You can add a well structured URI using the script in the scripts folder)
* Start Auction (It's necessary to add an expiration time, minimum bid and nft id)
* Bid (Bid on the desired auction)
* Withdraw overbidden bids (withdraw overbidden amounts)
* End Auction (callable only by the auctioneer)
* Withdraw not finalized (if the auctioneer does not finalized the auction within 24 hours after the expiration time, the winner can take his funds back)



## Technologies
Project is created with:
* Django: 4.0.3
* Djongo: 1.3.6
* Brownie: 1.19.2
* Web3.py: 5.28.0
	
## Setup
To run this project import the github folder and activate the virtual environment from your terminal.

!!! Contract needs to be compiled first.

To compile the contract open your brownie folder (after the activation of venv) and digit:
```
brownie compile
```

To deploy the smart contract simply digit the following on terminal:

```
brownie run scripts/deploy.py --network networkname 
```
User can actually deploy the contract on any eth related chain, but if the --network is not specified brownie will deploy it on the ganache-cli instance.

To test the contract simply digit:

```
brownie test
```
If the user want he can specify where to test the contract using the same syntax written to run the scripts.


Interaction with the contract is really easy, following instructions in terminal everytime you execute a transaction. You can either interact with an already deployed contract or deploy one on your own.


User can use the nft api to interact with the nft auction market contract and store in a mongo database all the events related to the contract. Using the http json response you can retrieve all the necessary information saved in the events.

