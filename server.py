import os, re
from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import MySQLConnector
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$")
app = Flask(__name__)
mysql = MySQLConnector(app, 'emaildb')
app.secret_key = os.urandom(24)


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/add", methods=["POST"])
def add():
	if len(request.form["email"]) < 1:
		flash("Please enter a valid email.")
		return redirect("/")

	elif not EMAIL_REGEX.match(request.form["email"]):
		flash("Email is not valid.")
		return redirect("/")

	else:
		query = "SELECT address FROM addresses WHERE address = :address"
		data = {"address":request.form["email"]
		}
		if mysql.query_db(query, data) != []:
			flash("That email already exists.")
			return redirect("/")

	session["new_email"] = request.form["email"]
	query = "INSERT INTO addresses (address, created_at, updated_at) VALUES (:address, NOW(), NOW())"
	data = {
		"address": request.form["email"],
	}
	mysql.query_db(query, data)
	return redirect("/success")

@app.route("/success")
def success():
	flash("The email address you entered ("+session["new_email"]+") is valid!")
	query = "SELECT address, DATE_FORMAT(created_at, '%c/%d/%y %l:%i %p') AS added_at FROM addresses"
	addresses = mysql.query_db(query)
	return render_template("success.html", all_addresses=addresses)

app.run(debug=True)