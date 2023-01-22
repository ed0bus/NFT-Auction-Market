import requests
import json
import fileinput

#use these two functions to first create the ipfs cid for your asset picture (load_file_to_ipfs) and second create a json ipfs with the previous cid stored inside


def load_json_to_ipfs(data_dict):
    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    payload = json.dumps(
        {
            "pinataOptions": {"cidVersion": 1},
            "pinataMetadata": {
                "name": "auctioned_nft",
            },
            "pinataContent": data_dict,
        }
    )

    headers = {
        "Content-Type": "application/json",
        "pinata_api_key": "6faaedfdda7482d0e2c5",
        "pinata_secret_api_key": "f250479abe46da62809a61aa863cffa2b4a44f5d70e685f601f22e84cee67e48",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    res = json.loads(response.text)
    ipfs_cid = res["IpfsHash"]
    return f"https://cloudflare-ipfs.com/ipfs/{ipfs_cid}"


# load
def load_file_to_ipfs():
    file = input("insert path of ur file:")
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    payload = {
        "pinataOptions": '{"cidVersion": 1}',
        "pinataMetadata": '{"name": "MyFile", "keyvalues": {"company": "Pinata"}}',
    }
    files = [
        (
            "file",
            (
                "img.png/jpg",
                open(
                    file,
                    "rb",
                ),
                "application/octet-stream",
            ),
        )
    ]
    headers = {
        "pinata_api_key": "6faaedfdda7482d0e2c5",
        "pinata_secret_api_key": "f250479abe46da62809a61aa863cffa2b4a44f5d70e685f601f22e84cee67e48",
    }

    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    res = json.loads(response.text)
    ipfs_cid = res["IpfsHash"]
    return f"https://cloudflare-ipfs.com/ipfs/{ipfs_cid}"


def erc721_metadata_json_schema(image_uri):
    name = input("Insert a name for your NFT:")
    description = input("Describe your nft details:")
    x = {
        "title": "Asset Metadata",
        "type": "Auction Object NFT",
        "properties": {
            "name": {"type": "string", "description": name},
            "description": {"type": "string", "description": description},
            "image": {"type": "string", "description": image_uri},
        },
    }
    return x
