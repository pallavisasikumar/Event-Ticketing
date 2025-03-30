from flask import *
from src.dbconnection import *

from web3 import Web3, HTTPProvider

# truffle development blockchain address
blockchain_address = 'http://127.0.0.1:7545'
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address,{"timeout": 800}))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = r"D:\blockchain\node_modules\.bin\build\contracts\VehicleHistory.json"
# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = '0x023Bb010F690cd03ED88Fb737250d45B6eb56F53'



app = Flask(__name__)

app.secret_key = "87497823"


@app.route("/login", methods=['post'])
def login():
    uname = request.form['uname']
    pswd = request.form['pswd']
    qry = "select * from login where username=%s and password=%s and type='seller'"
    val = (uname, pswd)
    res = selectone(qry, val)

    if res is None:
        return jsonify({"task":"failed"})
    else:
        return jsonify({"task":"valid", "id":res['id']})


@app.route("/view_event_details", methods=['post'])
def view_event_details():
    sid = request.form['lid']
    qry = "SELECT * FROM `event` WHERE seller_id = %s"
    res = selectall2(qry, sid)

    print(res)

    return jsonify(res)


@app.route("/view_ticket_details", methods=['post'])
def view_ticket_details():

    eid = request.form['eid']
    bid = request.form['bid']

    print(request.form)

    qry = "SELECT ename FROM `event` WHERE id = %s"
    res = selectone(qry, eid)
    event_name = res['ename']
    ctext = bid + "#" + event_name

    try:
        with open(r"D:\blockchain\node_modules\.bin\build\contracts\EventSystem.json") as file:
            contract_json = json.load(file)
            contract_abi = contract_json['abi']  # application binary interface

        contract = web3.eth.contract(address='0x023Bb010F690cd03ED88Fb737250d45B6eb56F53', abi=contract_abi)
        blocknumber = web3.eth.get_block_number()
        mdata = []

        print("Current Block Number:", blocknumber)

        for i in range(blocknumber, 3, -1):
            print(f"Processing Block {i}...")

            try:
                a = web3.eth.get_transaction_by_block(i, 0)
                decoded_input = contract.decode_function_input(a['input'])

                # if decoded_input[1]['bid'].split("#")[1] == event_name:

                if decoded_input[1]['bid'] == ctext:
                    data = {
                        'name': str(decoded_input[1]['name']),
                        'dob': str(decoded_input[1]['dob']),
                        'gender': str(decoded_input[1]['gender']),
                        'gov_id': str(decoded_input[1]['gov_id']),
                        'status': str(decoded_input[1]['status'])
                    }
                    mdata.append(data)
                    print(f"Updated data list: {mdata}")

            except Exception as e:
                print(f"Error Processing Block {i}: {e}")
                pass

    except Exception as e:
        print(f"Error with contract ABI or interaction: {e}")

    print("Final Collected Data:", mdata)


    return jsonify(mdata)


app.run(host="0.0.0.0", port="5000")