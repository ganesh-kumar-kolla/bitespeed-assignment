from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
 
app = Flask(__name__)
 
DATABASE = 'contacts.db'
 
@app.route('/identify', methods=['POST'])
def identify_contact():
    return "Hello, World!"
 
if __name__ == "__main__":
    app.run(host='127.0.0.1', port='5000', debug=True)