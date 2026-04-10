from flask import Flask, request, jsonify, render_template_string
from oracledb import cx_Oracle

app = Flask(__name__)

def get_connection():
    return cx_Oracle.connect(
        user="itlab18",
        password="itlab18",
        dsn="PSGCASLABS.labs-psgcas.com:1521/itora"
    )
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Login & Signup</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-5">

<h3>Login</h3>
<form id="loginForm">
<div class="mb-3">
<input type="text" class="form-control" name="username" placeholder="Username" required>
</div>
<div class="mb-3">
<input type="password" class="form-control" name="password" placeholder="Password" required>
</div>
<button type="submit" class="btn btn-primary">Login</button>
</form>

<hr>

<h3>Signup</h3>
<form id="signupForm">
<div class="mb-3">
<input type="text" class="form-control" name="username" placeholder="New Username" required>
</div>
<div class="mb-3">
<input type="password" class="form-control" name="password" placeholder="New Password" required>
</div>
<button type="submit" class="btn btn-success">Signup</button>
</form>

<div class="toast position-fixed bottom-0 end-0 p-3" id="liveToast">
<div class="toast-header">
<strong class="me-auto">Status</strong>
<button type="button" class="btn-close" data-bs-dismiss="toast"></button>
</div>
<div class="toast-body" id="toastMessage"></div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

<script>
document.getElementById("loginForm").addEventListener("submit", function(e) {
e.preventDefault();
let formData = new FormData(this);

fetch("/login",{method:"POST",body:formData})
.then(res=>res.json())
.then(data=>{
let toast = new bootstrap.Toast(document.getElementById('liveToast'));
document.getElementById('toastMessage').innerText =
data.status === "success" ? "Login Successful!" : "Invalid Username or Password!";
toast.show();
});
});

document.getElementById("signupForm").addEventListener("submit", function(e) {
e.preventDefault();
let formData = new FormData(this);

fetch("/signup",{method:"POST",body:formData})
.then(res=>res.json())
.then(data=>{
let toast = new bootstrap.Toast(document.getElementById('liveToast'));
document.getElementById('toastMessage').innerText =
data.status === "success" ? "Signup Successful!" : "Username already exists!";
toast.show();
});
});
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"].strip()
    password = request.form["password"].strip()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM usersmss
        WHERE TRIM(UPPER(id)) = :id_val AND TRIM(password) = :pwd_val
    """, {"id_val": username.upper(), "pwd_val": password})

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "fail"})

@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"].strip()
    password = request.form["password"].strip()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) FROM usersmss
        WHERE TRIM(UPPER(id)) = :id_val
    """, {"id_val": username.upper()})

    if cursor.fetchone()[0] > 0:
        cursor.close()
        conn.close()
        return jsonify({"status": "fail"})

    cursor.execute("""
        INSERT INTO usersmss (id, password)
        VALUES (:id_val, :pwd_val)
    """, {"id_val": username, "pwd_val": password})

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(debug=True)


