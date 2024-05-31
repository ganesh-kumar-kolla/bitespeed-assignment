from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
 
app = Flask(__name__)
 
DATABASE = 'contacts.db'

class ContactRequest:
    def __init__(self, email=None, phoneNumber=None):
        self.email = email
        self.phoneNumber = phoneNumber

class ContactResponse:
    def __init__(self, primaryContactId, emails, phoneNumbers, secondaryContactIds):
        self.primaryContactId = primaryContactId
        self.emails = emails
        self.phoneNumbers = phoneNumbers
        self.secondaryContactIds = secondaryContactIds

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
 
@app.route('/identify', methods=['POST'])
def identify_contact():
    data = request.get_json()
    email = data.get('email')
    phone_number = data.get('phoneNumber')

    if not email and not phone_number:
        return jsonify({"error": "Email or phone number must be provided."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to find related contacts
    if email and phone_number:
        cursor.execute('''
            SELECT * FROM contacts WHERE email = ? OR phoneNumber = ?
        ''', (email, phone_number))
    elif email:
        cursor.execute('''
            SELECT * FROM contacts WHERE email = ?
        ''', (email,))
    else:
        cursor.execute('''
            SELECT * FROM contacts WHERE phoneNumber = ?
        ''', (phone_number,))

    contacts = cursor.fetchall()

    if not contacts:
        # No contacts found, insert a new primary contact
        cursor.execute('''
            INSERT INTO contacts (phoneNumber, email, linkPrecedence, createdAt, updatedAt)
            VALUES (?, ?, 'primary', ?, ?)
        ''', (phone_number, email, datetime.utcnow(), datetime.utcnow()))
        conn.commit()
        
        new_contact_id = cursor.lastrowid

        response = ContactResponse(
            primaryContactId=new_contact_id,
            emails=[email] if email else [],
            phoneNumbers=[phone_number] if phone_number else [],
            secondaryContactIds=[]
        )
        return jsonify({"contact": response.__dict__})
 
if __name__ == "__main__":
    app.run(host='127.0.0.1', port='5000', debug=True)