from flask import *
from src.dbconnection import *
import functools
from werkzeug.utils import secure_filename
import os

from flask_mail import *
from email import encoders

import uuid



from web3 import Web3, HTTPProvider
# truffle development blockchain address
blockchain_address = 'http://127.0.0.1:7545'
# Client instance to interact with the blockchain
web3 = Web3(HTTPProvider(blockchain_address,{"timeout": 800}))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
compiled_contract_path = r"D:\blockchain\node_modules\.bin\build\contracts\EventSystem.json"
# Deployed contract address (see `migrate` command output: `contract address`)
deployed_contract_address = '0xc20C424ba44A751D7D032dfe47b6aAB1f2B7042b'
# Create your views here.
app = Flask(__name__) #flaskobject created


app.secret_key="00999875" #session use cheyn secret key


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'smartpass1216@gmail.com'
app.config['MAIL_PASSWORD'] = 'gdwf cqji ehtf sedt'

def login_required(func): # if lid not in session login pageilek ponm after logout
    @functools.wraps(func) #preserves metadata
    def secure_function():
        if "lid" not in session:
            return render_template('login_index.html')
        return func()

    return secure_function

@app.route('/')
def login():
    return render_template("login_index.html")                              # html page browseril load chykan


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route("/login_code",methods=['post'])
def login_code():
    username=request.form['textfield']
    password=request.form['textfield2']

    qry="SELECT * FROM login WHERE `username`=%s AND `password`=%s"
    val=(username,password)

    res=selectone(qry, val)
    if res is None:
        return '''<script>alert("Invalid Username or Password");window.location="/"</script>'''
    elif res['type'] == "admin":
        session['lid'] = res['id']
        return '''<script>alert("Welcome Admin");window.location="admin_home"</script>'''
    elif res['type'] == "seller":
        session['lid'] = res['id']
        return '''<script>alert("Welcome Seller");window.location="seller_home"</script>'''
    elif res['type'] == "user":
        session['lid'] = res['id']

        qry = "select * from user where lid = %s"
        res = selectone(qry, res['id'])

        session['state'] = res['state']

        return '''<script>alert("Welcome User");window.location="user_home"</script>'''
    else:
        return '''<script>alert("Invalid Username or Password");window.location="/"</script>'''


@app.route("/user_reg")
def user_reg():

    return render_template("user_register.html")


@app.route("/registration_code", methods=['post'])
def registration_code():
    try:
        name = request.form['name']
        place=request.form['place']
        post=request.form['post']
        pin=request.form['pincode']

        state = request.form['state']

        ph_no=request.form['phone']
        email=request.form['email']
        username=request.form['username']
        password=request.form['password']

        qry = "SELECT * FROM `login` WHERE `username`=%s"
        res = selectone(qry, username)

        if res is None:

            qry = "INSERT INTO login VALUES(NULL,%s,%s,'user')"
            id = iud(qry,(username,password))

            qry = "INSERT INTO USER VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,%s)"
            iud(qry,(id, name, place, post, pin, state, ph_no, email))

            return '''<script>alert("Successfully registered");window.location="/"</script>'''
        else:
            return '''<script>alert("Username already exists");window.location="/"</script>'''

    except Exception as e:
        return '''<script>alert("Email or phone already exists");window.location="/"</script>'''


@app.route("/seller_reg")
def seller_reg():

    return render_template("seller_register.html")


@app.route("/seller_registration_code", methods=['post'])
def seller_registration_code():
    try:
        name = request.form['name']
        place=request.form['place']
        post=request.form['post']
        pin=request.form['pincode']
        ph_no=request.form['phone']
        email=request.form['email']
        username=request.form['username']
        password=request.form['password']

        qry = "SELECT * FROM `login` WHERE `username`=%s"
        res = selectone(qry, username)

        if res is None:

            qry = "INSERT INTO login VALUES(NULL,%s,%s,'pending')"
            id = iud(qry,(username,password))

            qry = "INSERT INTO SELLER VALUES(NULL,%s,%s,%s,%s,%s,%s,%s)"
            iud(qry,(id, name, place, post, pin, ph_no, email))

            return '''<script>alert("Successfully registered");window.location="/"</script>'''
        else:
            return '''<script>alert("Username already exists");window.location="/"</script>'''

    except Exception as e:
        print("======="+str(e))
        return '''<script>alert("Email or phone already exists");window.location="/"</script>'''


@app.route("/admin_home")
@login_required
def admin_home():
    return render_template("admin/admin_index.html")


@app.route("/verify_seller")
@login_required
def verify_seller():
    qry = "SELECT `login`.id, `seller`.* FROM `seller` JOIN `login` ON `seller`.`lid`=`login`.id WHERE `login`.type='pending'"
    res = selectall(qry)
    print(res)
    return render_template("admin/verify seller.html", val=res)


@app.route("/accept_seller")
@login_required
@login_required
def accept_seller():
    id = request.args.get('id')
    qry = "UPDATE `login` SET TYPE='seller' WHERE id=%s"
    iud(qry, id)
    return '''<script>alert("Accepted");window.location="/verify_seller"</script>'''


@app.route("/reject_seller")
@login_required
def reject_seller():
    id = request.args.get('id')
    qry = "UPDATE `login` SET TYPE='reject' WHERE id=%s"
    iud(qry, id)
    return '''<script>alert("Rejected");window.location="/verify_seller"</script>'''


@app.route("/view_report")
@login_required
def view_report():
    qry= "SELECT `user`.name, `event`.ename, `reports`.*, `seller`.name AS sname FROM `reports` JOIN `user` ON `reports`.lid=`user`.lid JOIN `event` ON `reports`.eid=`event`.id join `seller` ON `event`.`seller_id`=`seller`.lid WHERE `reports`.Action = 'pending'"
    res = selectall(qry)

    return render_template("admin/view_scam_reports.html", val = res)



@app.route("/take_action")
def take_action():
    id = request.args.get('id')
    session['report_id'] = id

    lid = request.args.get("lid")
    session['userid'] = lid

    eid = request.args.get('eid')
    session['evntid'] = eid
    return render_template("admin/takeaction.html")


@app.route("/submit_action", methods=['post'])
def submit_action():
    action = request.form['action']
    remarks = request.form['remarks']

    qry = "SELECT email FROM `user` WHERE lid=%s"
    user_email = selectone(qry, session['userid'])

    qry = "SELECT lid,email FROM `seller` JOIN `event` ON `seller`.lid = `event`.seller_id WHERE `event`.id = %s"
    seller_email = selectone(qry, session['evntid'])


    def mail(email, subject):
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)
            gmail.ehlo()                                #establishing the smtp connection
            gmail.starttls()                            #start tls encryption
            gmail.login('smartpass1216@gmail.com', 'gdwf cqji ehtf sedt')
        except Exception as e:
            print("Couldn't setup email!!" + str(e))
        msg = MIMEText(remarks)                 #creates an email body
        print(msg)
        msg['Subject'] = subject
        msg['To'] = email
        msg['From'] = 'smartpass1216@gmail.com'
        try:
            gmail.send_message(msg)
        except Exception as e:
            print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert("Success");window.location="/view_report"</script>'''

    if action == "warning":
        qry = "UPDATE `reports` SET ACTION='warned seller' WHERE id=%s"
        iud(qry, session['report_id'])

        mail(seller_email['email'], "Scam report recieved ")
        mail(user_email['email'], "Copy of action of your report")
        return '''<script>alert("Success");window.location="/view_report"</script>'''

    elif action == "ban":
        qry = "UPDATE `reports` SET ACTION='Seller Banned' WHERE id=%s"
        iud(qry, session['report_id'])

        mail(seller_email['email'], "Your account has been banned")
        mail(user_email['email'], "Thanks for your report.")

        qry = "UPDATE `login` SET TYPE='banned' WHERE id=%s"
        iud(qry, seller_email['lid'])
        return '''<script>alert("Success");window.location="/view_report"</script>'''

    else:
        mail(user_email['email'], "Report Ignored")
        return '''<script>alert("Success");window.location="/view_report"</script>'''


    return '''<script>alert("Success");window.location="/view_report"</script>'''


@app.route("/seller_home")
@login_required
def seller_home():
    return render_template("seller/seller_index.html")


@app.route("/manage_events")
@login_required
def manage_events():
    # qry = "SELECT `tickets`.id AS tid, `event`.* FROM `event` JOIN `tickets` ON `event`.`id`=`tickets`.eid WHERE `event`.`seller_id`=%s"
    # res = selectall2(qry, session['lid'])

    qry = "SELECT * FROM `event` WHERE `seller_id`=%s"
    res = selectall2(qry, session['lid'])

    return render_template("seller/manage_events.html", val=res)


@app.route("/edit_event")
def edit_event():
    id = request.args.get('id')
    session['e_event_id'] = id

    qry = "SELECT * FROM `event` WHERE id = %s"
    res = selectone(qry, id)

    return render_template("Seller/edit_event_details.html", val = res)


@app.route("/update_event", methods=['post'])
def update_event():
    try:
        name = request.form['textfield']
        details = request.form['textfield2']
        date = request.form['textfield3']
        venue = request.form['textfield4']

        location = request.form['location']
        event_type = request.form['type']
        image = request.files['file']

        # Save image securely
        image_name = secure_filename(image.filename)
        image_path = os.path.join('static/uploads', image_name)
        image.save(image_path)

        qry = "UPDATE `event` SET `ename`=%s, `details`=%s, `venue`=%s, `location`=%s, `image`=%s, `date`=%s, `type`=%s WHERE `id` = %s"
        iud(qry, (name, details, venue, location, image_name, date, event_type, session['e_event_id']))

        return '''<script>alert("Edited");window.location="/manage_events"</script>'''

    except:
        name = request.form['textfield']
        details = request.form['textfield2']
        date = request.form['textfield3']
        venue = request.form['textfield4']

        location = request.form['location']
        event_type = request.form['type']


        qry = "UPDATE `event` SET `ename`=%s, `details`=%s, `venue`=%s, `location`=%s, `date`=%s, `type`=%s WHERE `id` = %s"
        iud(qry, (name, details, venue, location, date, event_type, session['e_event_id']))

        return '''<script>alert("Edited");window.location="/manage_events"</script>'''


@app.route("/delete_event")
@login_required
def delete_event():
    id = request.args.get("id")
    qry = "DELETE FROM `event` WHERE id=%s"
    iud(qry, id)
    return '''<script>alert("Deleted");window.location="/manage_events"</script>'''


@app.route("/add_event_details", methods=['post'])
@login_required
def add_event_details():
    return render_template("Seller/add_event_details.html")


@app.route("/insert_event_details", methods=['POST'])
@login_required
def insert_event_details():
    try:
        # Get form values
        name = request.form['textfield']
        details = request.form['textfield2']
        date = request.form['textfield3']
        venue = request.form['textfield4']
        number_of_tickets = int(request.form['textfield5'])
        price = request.form['textfield6']
        location = request.form['location']
        event_type = request.form['type']
        image = request.files['file']

        # Save image securely
        image_name = secure_filename(image.filename)
        image_path = os.path.join('static/uploads', image_name)
        image.save(image_path)

        # Insert event details
        event_query = "INSERT INTO `event` VALUES (null, %s, %s, %s, %s, %s, %s, %s, %s)"
        event_id = iud(event_query, (session['lid'], name, details, venue, location, image_name, date, event_type))
       # print(f"Inserted Event ID: {event_id}")

        # Insert tickets
        ticket_query = "INSERT INTO `tickets` VALUES (%s, %s, 'available', %s)"

        for i in range(number_of_tickets):
            ticket_id = str(uuid.uuid4())  # Generate a unique ticket ID

            try:
                iud(ticket_query, (ticket_id, event_id, price))
            except Exception as e:
                print(f"❌ Ticket {i + 1} failed: {e}")

        return '''<script>alert("Successfully added");window.location="/manage_events"</script>'''

    except Exception as e:
        print(f"Error: {str(e)}")
        return f'''<script>alert("Error: {str(e)}");window.location="/manage_events"</script>'''


@app.route("/manage_ticket")
@login_required
def manage_ticket():
    id = request.args.get('id')
    qry = "SELECT count(*) as total FROM `tickets` WHERE eid=%s"
    res = selectone(qry, id)

    qry = "SELECT count(*) as booked FROM `tickets` WHERE eid=%s AND status='booked'"
    res2 = selectone(qry, id)

    qry = "SELECT count(*) as available FROM `tickets` WHERE eid=%s AND status='available'"
    res3 = selectone(qry, id)

    return render_template("seller/manage_tickets.html", val=res, val2=res2, val3=res3)

# @app.route("/edit_ticket")
# @login_required
# def edit_ticket():
#     tid = request.args.get('tid')
#     session['tid'] = tid
#     qry = "SELECT * FROM `tickets` WHERE id =%s"
#     res = selectone(qry, tid)
#     return render_template("Seller/edit_ticket.html", val=res['ticket'])
#
#
# @app.route("/update_ticket", methods=['post'])
# @login_required
# def update_ticket():
#     ticket = request.form['textfield']
#     qry = "UPDATE `tickets` SET `ticket`=%s WHERE `id`=%s"
#     iud(qry, (ticket, session['tid']))
#
#     return '''<script>alert("Successfully Edited");window.location="manage_events"</script>'''


@app.route("/view_bookings")
@login_required
def view_bookings():
    qry = "SELECT `user`.name, `event`.ename, `booking`.* FROM `booking` JOIN `user` ON `booking`.lid = `user`.lid JOIN `event` ON `booking`.eid=`event`.id WHERE `event`.`seller_id`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("Seller/view_bookings.html", val=res)


@app.route("/view_bookings_details")
def view_bookings_details():
    id = request.args.get('id')
    data = seller_view_booking_details(id)

    return render_template("Seller/booking_details.html", val = data)


def seller_view_booking_details(id):

    qry = "SELECT * FROM `booking` WHERE id = %s"
    booking = selectone(qry, id)

    qry="SELECT ename FROM `event` WHERE id = %s"
    res = selectone(qry, booking['eid'])
    event_name = res['ename']
    ctext = id + "#" + event_name

    try:
        with open(r"D:\blockchain\node_modules\.bin\build\contracts\EventSystem.json") as file:
            contract_json = json.load(file)
            contract_abi = contract_json['abi'] #application binary interface

        contract = web3.eth.contract(address='0xc20C424ba44A751D7D032dfe47b6aAB1f2B7042b', abi=contract_abi)
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
                        'gov_id_type': str(decoded_input[1]['gov_id_type']),
                        'gov_id': str(decoded_input[1]['gov_id'])
                    }
                    mdata.append(data)
                    print(f"Updated data list: {mdata}")

            except Exception as e:
                print(f"Error Processing Block {i}: {e}")
                pass

    except Exception as e:
        print(f"Error with contract ABI or interaction: {e}")

    print("Final Collected Data:", mdata)

    return mdata



@app.route("/view_cancellation")
@login_required
def view_cancellation():
    qry = "SELECT `user`.name, `event`.ename, `booking_cancellation`.* FROM `booking_cancellation` JOIN `booking` ON `booking_cancellation`.bid = `booking`.id JOIN `event` ON  `booking`.eid = `event`.id JOIN `user` ON `booking`.lid = `user`.lid WHERE `event`.`seller_id`=%s"
    res = selectall2(qry, session['lid'])

    return render_template("Seller/view_cancellation.html", val = res)


@app.route("/user_home")
@login_required
def user_home():
    return render_template("user/user_index.html")


@app.route("/choose_event")
@login_required
def choose_event():

    qry = "SELECT * FROM `event` WHERE location = %s AND DATE > CURDATE()"
    res = selectall2(qry, session['state'])

    print(res)

    return render_template("user/choose_event.html" , val = res)


@app.route("/get_selected_option", methods=['post'])
@login_required
def get_selected_option():
    selected_type = request.form.get("type")
    print(selected_type)
    location = request.form['location']

    qry = "SELECT * FROM `event` WHERE `location`=%s AND `type`=%s"
    res = selectall2(qry, (location, selected_type))

    print(res)

    return render_template("user/view_events.html", val=res)


@app.route("/purchase_ticket")
def purchase_ticket():
    id = request.args.get('id')
    session['eid'] = id

    qry = "SELECT * FROM `event` WHERE id=%s"
    res = selectone(qry, id)

    qry = "SELECT COUNT(*) as count, price FROM `tickets` WHERE eid=%s and status='available'"
    res2 = selectone(qry, id)

    return render_template("user/purchase ticket.html", event = res, ticket = res2["count"], price = res2['price'])


@app.route("/process_booking", methods=['POST'])
def process_booking():
    num_tickets = int(request.form.get("num_tickets", 0))

    tickets = []
    for i in range(1, num_tickets + 1):
        name = request.form.get(f"name_{i}")
        dob = request.form.get(f"dob_{i}")
        gender = request.form.get(f"gender_{i}")
        gov_type = request.form.get(f"gov_type_{i}")
        gov_id = request.form.get(f"gov_id_{i}")

        tickets.append({"name": name, "dob": dob, "gender": gender, "gov_type" : gov_type, "gov_id" : gov_id})

    print(tickets)

    # Fetch available ticket IDs from the tickets table
    qry = "SELECT id FROM `tickets` WHERE `status`='available' and eid = %s LIMIT %s"
    ticket_ids = selectall2(qry, (session['eid'],num_tickets))

    print("====count", len(ticket_ids))

    # If the number of available tickets doesn't match the requested number, show an error
    if len(ticket_ids) != num_tickets:
        return '''<script>alert("Not enough available tickets!");window.location="/user_home"</script>'''

    else:

        # Insert into booking table

        qry = "SELECT * FROM `booking` WHERE eid = %s AND lid=%s"
        booking_res = selectone(qry, (session['eid'], session['lid']))

        if booking_res is None:

            qry = "INSERT INTO `booking` VALUES(NULL, %s, %s, %s, CURDATE())"
            bid = iud(qry, (session['lid'], session['eid'], num_tickets))  # Get booking ID

            import qrcode

            # Data to encode
            data = bid

            # Create a QR code object
            qr = qrcode.QRCode(
                version=1,  # Controls the size of the QR code
                error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
                box_size=10,  # Size of each box in pixels
                border=4  # Border size
            )

            qr.add_data(data)
            qr.make(fit=True)

            # Create an image from the QR Code instance
            img = qr.make_image(fill="black", back_color="white")

            image_path = os.path.join('static/qr', str(bid)+".jpg")
            img.save(image_path)


        else:
            bid = booking_res['id']
            qry = "UPDATE `booking` SET `ticket_count` = `ticket_count`+%s WHERE id = %s"
            iud(qry, (int(num_tickets) , bid))

        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # load contract info as JSON
            contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

        # Insert ticket details into booking_details table
        qry = "INSERT INTO `booking_details` VALUES(null, %s, %s, %s, %s, %s)"
        for i, ticket in enumerate(tickets):
            ticket_id = ticket_ids[i]['id']

            res_evnt = selectone("SELECT ename FROM `event` WHERE id = %s", session['eid'])

            Event_name = res_evnt['ename']

            iud(qry, (bid, ticket['name'], ticket['dob'], ticket['gender'], ticket_id))  # Insert each ticket with its ID
            try:


                blocknumber = web3.eth.get_block_number()
                message2 = contract.functions.addreq(blocknumber + 1, str(bid)+"#"+Event_name, ticket['name'], ticket['dob'], ticket['gender'], ticket_id, ticket['gov_type'] ,ticket['gov_id'], "unused"
                                                      ).transact({'from': web3.eth.accounts[0]})

                print(message2)


            except Exception as e:
                print(str(e))

        # Update the ticket status to 'booked' for each assigned ticket
        for ticket_id in ticket_ids:
            qry = "UPDATE `tickets` SET `status`='booked' WHERE `id`=%s"
            iud(qry, (ticket_id['id'],))  # Mark the ticket as booked

        return '''<script>alert("Successfully Booked");window.location="/user_home"</script>'''


@app.route("/manage_bookings")
def manage_bookings():
    qry = "SELECT event.`ename`,`details`,`venue`,`location`,`image`,event.`date`, `event`.id AS eid ,`event`.seller_id AS sid ,`booking`.id,`ticket_count`,booking.`date` AS booking_date FROM `event` JOIN `booking`ON `event`.id=`booking`.eid WHERE `booking`.lid=%s"
    res = selectall2(qry, session['lid'])

    res2 = "NONE"

    if len(res)!=0:

        sid = res[0]['sid']

        qry = "SELECT * FROM `seller` WHERE lid=%s"
        res2 = selectone(qry, sid)

    return render_template("user/manage_booking.html", events = res, seller = res2)


@app.route("/view_booking_details")
def view_booking_details():
    id = request.args.get("id")
    eid = request.args.get('eid')
    qry = "SELECT `details` FROM `event` WHERE `id`=%s"
    res2 = selectone(qry, eid)

    details = view_details(eid, id)

    qr = str(id)+".jpg"

    return render_template("user/booking_details.html", val=details, details = res2['details'], qrcode = qr)


@app.route("/report_scam")
def report_scam():
    id = request.args.get("id")
    session['r_e_id'] = id
    return render_template("user/report_scam.html")


@app.route("/submit_scam", methods=['post'])
def submit_scam():
    details = request.form['description']

    qry = "INSERT INTO `reports` VALUES(null, %s, %s, %s, CURDATE(), 'pending')"
    iud(qry, (session['lid'], session['r_e_id'], details))

    return '''<script>alert("Reported");window.location="choose_event"</script>'''


def view_details(eid, id):
    # Retrieve the user ID from session

    qry="SELECT ename FROM `event` WHERE id = %s"
    res = selectone(qry, eid)
    event_name = res['ename']
    ctext = id + "#" + event_name

    try:
        with open(r"D:\blockchain\node_modules\.bin\build\contracts\EventSystem.json") as file:
            contract_json = json.load(file)
            contract_abi = contract_json['abi']

        contract = web3.eth.contract(address='0xc20C424ba44A751D7D032dfe47b6aAB1f2B7042b', abi=contract_abi)
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
                        'gov_id_type': str(decoded_input[1]['gov_id_type']),
                        'gov_id': str(decoded_input[1]['gov_id'])
                    }
                    mdata.append(data)
                    print(f"Updated data list: {mdata}")

            except Exception as e:
                print(f"Error Processing Block {i}: {e}")
                pass

    except Exception as e:
        print(f"Error with contract ABI or interaction: {e}")

    print("Final Collected Data:", mdata)

    return mdata  # Return data as a normal list, not as JSON


app.run(debug=True)

