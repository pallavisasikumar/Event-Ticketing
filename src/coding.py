from flask import *
from src.dbconnection import *
import functools
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)


app.secret_key="00999875"


def login_required(func):
    @functools.wraps(func)
    def secure_function():
        if "lid" not in session:
            return render_template('login_index.html')
        return func()

    return secure_function

@app.route('/')
def login():
    return render_template("login_index.html")


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
        ph_no=request.form['phone']
        email=request.form['email']
        username=request.form['username']
        password=request.form['password']

        qry = "SELECT * FROM `login` WHERE `username`=%s"
        res = selectone(qry, username)

        if res is None:

            qry = "INSERT INTO login VALUES(NULL,%s,%s,'user')"
            id = iud(qry,(username,password))

            qry = "INSERT INTO USER VALUES(NULL,%s,%s,%s,%s,%s,%s,%s)"
            iud(qry,(id, name, place, post, pin, ph_no, email))

            return '''<script>alert("Successfully registered");window.location="/"</script>'''
        else:
            return '''<script>alert("Username already exists");window.location="/"</script>'''

    except Exception as e:
        print("======="+str(e))
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
def admin_home():
    return render_template("admin/admin_index.html")


@app.route("/verify_seller")
def verify_seller():
    qry = "SELECT `login`.id, `seller`.* FROM `seller` JOIN `login` ON `seller`.`lid`=`login`.id WHERE `login`.type='pending'"
    res = selectall(qry)
    print(res)
    return render_template("admin/verify seller.html", val=res)


@app.route("/accept_seller")
@login_required
def accept_seller():
    id = request.args.get('id')
    qry = "UPDATE `login` SET TYPE='seller' WHERE id=%s"
    iud(qry, id)
    return '''<script>alert("Accepted");window.location="/verify_seller"</script>'''


@app.route("/reject_seller")
@login_required
def reject_sellerlph():
    id = request.args.get('id')
    qry = "UPDATE `login` SET TYPE='reject' WHERE id=%s"
    iud(qry, id)
    return '''<script>alert("Rejected");window.location="/verify_seller"</script>'''


@app.route("/view_report")
def view_report():
    qry= "SELECT `user`.name, `event`.ename, `reports`.*, `seller`.name AS sname FROM `reports` JOIN `user` ON `reports`.lid=`user`.lid JOIN `event` ON `reports`.eid=`event`.id join `seller` ON `event`.`seller_id`=`seller`.lid WHERE `reports`.Action = 'pending'"
    res = selectall(qry)

    return render_template("admin/view_scam_reports.html", val = res)


@app.route("/seller_home")
def seller_home():
    return render_template("seller/seller_index.html")


@app.route("/manage_events")
def manage_events():
    qry = "SELECT `tickets`.id AS tid, `event`.* FROM `event` JOIN `tickets` ON `event`.`id`=`tickets`.eid WHERE `event`.`seller_id`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("seller/manage_events.html", val=res)


@app.route("/delete_event")
def delete_event():
    id = request.args.get("id")
    qry = "DELETE FROM `event` WHERE id=%s"
    iud(qry, id)
    return '''<script>alert("Deleted");window.location="/manage_events"</script>'''


@app.route("/add_event_details", methods=['post'])
def add_event_details():
    return render_template("Seller/add_event_details.html")


@app.route("/insert_event_details", methods=['post'])
def insert_event_details():
    name = request.form['textfield']
    details = request.form['textfield2']
    date = request.form['textfield3']
    venue = request.form['textfield4']
    number_of_ticket = request.form['textfield5']
    price = request.form['textfield6']
    location = request.form['location']
    type = request.form['type']
    image = request.files['file']

    image_name = secure_filename(image.filename)
    image.save(os.path.join('static/uploads', image_name))

    qry = "INSERT INTO `event` VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,%s)"
    id = iud(qry, (session['lid'], name, details, venue, location, image_name, date, type))

    qry = "INSERT INTO `tickets` VALUES(NULL, %s, %s, %s)"
    iud(qry, (id, number_of_ticket, price))

    return '''<script>alert("Successfully added");window.location="/manage_events"</script>'''


@app.route("/manage_ticket")
def manage_ticket():
    id = request.args.get('id')
    qry = "SELECT * FROM `tickets` WHERE eid=%s"
    res = selectall2(qry, id)

    return render_template("seller/manage_tickets.html", val=res)

@app.route("/edit_ticket")
def edit_ticket():
    tid = request.args.get('tid')
    session['tid'] = tid
    qry = "SELECT * FROM `tickets` WHERE id =%s"
    res = selectone(qry, tid)
    return render_template("Seller/edit_ticket.html", val=res['ticket'])


@app.route("/update_ticket", methods=['post'])
def update_ticket():
    ticket = request.form['textfield']
    qry = "UPDATE `tickets` SET `ticket`=%s WHERE `id`=%s"
    iud(qry, (ticket, session['tid']))

    return '''<script>alert("Successfully Edited");window.location="manage_events"</script>'''


@app.route("/view_bookings")
def view_bookings():
    qry = "SELECT `user`.name, `event`.ename, `booking`.* FROM `booking` JOIN `user` ON `booking`.lid = `user`.lid JOIN `event` ON `booking`.eid=`event`.id WHERE `event`.`seller_id`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("Seller/view_bookings.html", val=res)


@app.route("/view_cancellation")
def view_cancellation():
    qry = "SELECT `user`.name, `event`.ename, `booking_cancellation`.* FROM `booking_cancellation` JOIN `booking` ON `booking_cancellation`.bid = `booking`.id JOIN `event` ON  `booking`.eid = `event`.id JOIN `user` ON `booking`.lid = `user`.lid WHERE `event`.`seller_id`=%s"
    res = selectall2(qry, session['lid'])

    return render_template("Seller/view_cancellation.html", val = res)


@app.route("/user_home")
def user_home():
    return render_template("user/user_index.html")


@app.route("/choose_event")
def choose_event():
    return render_template("user/choose_event.html")


@app.route("/get_selected_option", methods=['post'])
def get_selected_option():
    selected_type = request.form.get("type")
    print(selected_type)
    return render_template("user/select_event.html")


app.run(debug=True)

