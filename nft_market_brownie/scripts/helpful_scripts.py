from brownie import network, accounts, config

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

#get the proper account when you test or execute your scripts
def get_account(x):
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
    ):  # the network keyword allows us to intercat with different networks
        return accounts[x]
    else:
        return accounts.add(config["wallets"]["from_key"])
