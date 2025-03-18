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
deployed_contract_address = '0x32184435B76004211EA806A324945C2aC39Da478'



app = Flask(__name__)

app.secret_key = "87497823"

@app.route("/")
def home():
    return "ok"

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

    return jsonify(res)


app.run(host="0.0.0.0", port="5000")