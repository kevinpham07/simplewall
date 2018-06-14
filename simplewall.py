from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re
app = Flask(__name__)
app.secret_key = "asdf"
bcrypt = Bcrypt(app)

mysql = connectToMySQL("logregdb")

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route("/")
def loginpage():
	return render_template("login.html")

@app.route("/login", methods = ["post"])
def login():
	query = "SELECT * FROM users WHERE email = %(email)s;"
	data = {
		"email": request.form["email"]
	}
	result = mysql.query_db(query, data)
	if result:
		if bcrypt.check_password_hash(result[0]["password"], request.form["password"]):
			session["logged.in"] = True
			session["name"] = result[0]["first_name"]
			session["userid"] = result[0]["id"]
			return redirect("/wall")
	flash("Wrong email/password")
	return redirect("/")

@app.route("/wall")
def simplewall():
	if session["logged.in"] != True:
		return redirect("/")
	if "name" not in session:
		return redirect("/")
	if "userid" not in session:
		return redirect("/")
	abc = "SELECT COUNT(*) AS messages FROM messages WHERE user_id = %(id)s;"
	asdf = {
		"id": session["userid"]
	}
	count = mysql.query_db(abc, asdf)

	abc1 = "SELECT COUNT(*) AS messages FROM messages WHERE friend_id = %(id)s;"
	asdf1 = {
		"id": session["userid"]
	}
	count1 = mysql.query_db(abc1, asdf1)

	query = "SELECT * FROM users WHERE id <> %(id)s;"
	data = {
		"id": session["userid"]
	}
	uid = mysql.query_db(query, data)

	messages = "SELECT * FROM messages JOIN users ON messages.user_id = users.id WHERE friend_id = %(id)s;"
	msgdata = {
		"id": session["userid"]
	}
	messages = mysql.query_db(messages, msgdata)

	return render_template("simplewall.html", unique = uid, count = count, msg = messages, count1 = count1)

@app.route("/message", methods = ["post"])
def message():
	query = "INSERT INTO messages (content, created_at, user_id, friend_id) VALUES (%(content)s, NOW(), %(user_id)s, %(friend_id)s);"
	data = {
		"content": request.form["message"],
		"user_id": session["userid"],
		"friend_id": request.form["friend_id"]
	}
	mysql.query_db(query, data)
	return redirect("/wall")

@app.route("/logout")
def logout():
	session["logged.in"] = False
	session.pop("name")
	session.pop("userid")
	return redirect("/")

@app.route("/delete/<did>")
def delete(did):
	query1 = "SELECT * FROM messages WHERE id = %(id)s;"
	data1 = {
		"id": did
	}
	id = mysql.query_db(query1, data1)
	if session["userid"] != id[0]["friend_id"] or session["userid"] != id[0]["user_id"]:
		redirect("/danger")
	query = "DELETE FROM messages WHERE id = %(id)s;"
	data = {
		"id": did
	}
	mysql.query_db(query, data)
	return redirect("/wall")

@app.route("/danger")
def danger():
	return render_template("danger.html")

if __name__ == "__main__":
	app.run(debug = True)