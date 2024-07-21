from flask import Flask, render_template, request, redirect, url_for, flash
import os
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = TinyDB('accounts.json')
User = Query()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        username = request.form['username']
        initial_deposit = float(request.form['initial_deposit'])

        if initial_deposit < 0:
            flash("Initial deposit cannot be negative.", "error")
            return redirect(url_for('create_account'))

        if db.search(User.account_number == account_number):
            flash("Account number already exists.", "error")
            return redirect(url_for('create_account'))

        db.insert({'account_number': account_number, 'username': username, 'balance': initial_deposit})
        flash("Account created successfully!", "success")
        return redirect(url_for('index'))
    return render_template('create_account.html')

@app.route('/view_balance', methods=['GET', 'POST'])
def view_balance():
    if request.method == 'POST':
        account_number = request.form['account_number']
        account = db.get(User.account_number == account_number)
        if not account:
            flash("Account not found.", "error")
            return redirect(url_for('view_balance'))
        return render_template('view_balance.html', account=account)
    return render_template('view_balance.html')

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])

        if amount <= 0:
            flash("Deposit amount must be positive.", "error")
            return redirect(url_for('deposit'))

        account = db.get(User.account_number == account_number)
        if not account:
            flash("Account not found.", "error")
            return redirect(url_for('deposit'))

        new_balance = account['balance'] + amount
        db.update({'balance': new_balance}, User.account_number == account_number)
        flash(f"Deposited {amount} successfully!", "success")
        return redirect(url_for('index'))
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])

        if amount <= 0:
            flash("Withdrawal amount must be positive.", "error")
            return redirect(url_for('withdraw'))

        account = db.get(User.account_number == account_number)
        if not account:
            flash("Account not found.", "error")
            return redirect(url_for('withdraw'))

        if account['balance'] < amount:
            flash("Insufficient balance.", "error")
            return redirect(url_for('withdraw'))

        new_balance = account['balance'] - amount
        db.update({'balance': new_balance}, User.account_number == account_number)
        flash(f"Withdrawn {amount} successfully!", "success")
        return redirect(url_for('index'))
    return render_template('withdraw.html')

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        if db.remove(User.account_number == account_number):
            flash("Account deleted successfully!", "success")
        else:
            flash("Account not found.", "error")
        return redirect(url_for('index'))
    return render_template('delete_account.html')

if __name__ == '__main__':
    app.run(debug=True)