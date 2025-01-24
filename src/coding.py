from flask import *
from src.dbconnection import *
import functools
from werkzeug.utils import secure_filename

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
    qry= "SELECT `user`.name, `event`.ename, `reports`.* FROM `reports` JOIN `user` ON `reports`.lid=`user`.lid JOIN `event` ON `reports`.eid=`event`.id WHERE `reports`.Action = 'pending'"
    res = selectall(qry)

    return render_template("admin/view_scam_reports.html", val = res)


@app.route("/seller_home")
def seller_home():
    return render_template("seller/seller_index.html")


app.run(debug=True)

