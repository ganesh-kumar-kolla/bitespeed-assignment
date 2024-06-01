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
 

    # Find primary contact and gather information
    contacts = [dict(contact) for contact in contacts]

    # Get all linked contacts
    linked_ids = set()
    for contact in contacts:
        if contact['linkedId']:
            linked_ids.add(contact['linkedId'])
        else:
            linked_ids.add(contact['id'])

    linked_contacts = []
    for linked_id in linked_ids:
        cursor.execute('SELECT * FROM contacts WHERE id = ? OR linkedId = ?', (linked_id, linked_id))
        linked_contacts.extend(cursor.fetchall())

    linked_contacts = [dict(contact) for contact in linked_contacts]
    primary_contact = min(linked_contacts, key=lambda c: c['createdAt'])
    primary_id = primary_contact['id']

    existing_emails = {contact['email'] for contact in linked_contacts if contact['email']}
    existing_phone_numbers = {contact['phoneNumber'] for contact in linked_contacts if contact['phoneNumber']}

    new_email = email and email not in existing_emails
    new_phone_number = phone_number and phone_number not in existing_phone_numbers

    if new_email or new_phone_number:
        cursor.execute('''
            INSERT INTO contacts (phoneNumber, email, linkedId, linkPrecedence, createdAt, updatedAt)
            VALUES (?, ?, ?, 'secondary', ?, ?)
        ''', (phone_number, email, primary_id, datetime.utcnow(), datetime.utcnow()))
        conn.commit()
        
        new_contact_id = cursor.lastrowid
        if new_email:
            existing_emails.add(email)
        if new_phone_number:
            existing_phone_numbers.add(phone_number)

        # Re-query all linked contacts to ensure all secondary contacts are correctly included
        cursor.execute('SELECT * FROM contacts WHERE id = ? OR linkedId = ?', (primary_id, primary_id))
        linked_contacts = cursor.fetchall()

    # Check if the new contact should become the primary contact
    if new_email or new_phone_number:
        if new_email and new_phone_number:
            cursor.execute('SELECT * FROM contacts WHERE email = ? OR phoneNumber = ?', (email, phone_number))
            new_contacts = cursor.fetchall()
            new_contacts = [dict(contact) for contact in new_contacts]
            new_primary_contact = min(new_contacts, key=lambda c: c['createdAt'])
            if new_primary_contact['id'] != primary_id:
                # Update link precedence
                cursor.execute('UPDATE contacts SET linkPrecedence = "secondary" WHERE id = ?', (primary_id,))
                cursor.execute('UPDATE contacts SET linkPrecedence = "primary" WHERE id = ?', (new_primary_contact['id'],))
                primary_id = new_primary_contact['id']

    # Collect all unique emails and phone numbers
    primary_email = primary_contact['email']
    primary_phone_number = primary_contact['phoneNumber']
    
    all_emails = [primary_email] if primary_email else []
    all_emails.extend([contact['email'] for contact in linked_contacts if contact['email'] and contact['email'] != primary_email])
    
    all_phone_numbers = [primary_phone_number] if primary_phone_number else []
    all_phone_numbers.extend([contact['phoneNumber'] for contact in linked_contacts if contact['phoneNumber'] and contact['phoneNumber'] != primary_phone_number])

    secondary_ids = [contact['id'] for contact in linked_contacts if contact['id'] != primary_id]

    response = ContactResponse(
        primaryContactId=primary_id,
        emails=all_emails,
        phoneNumbers=all_phone_numbers,
        secondaryContactIds=secondary_ids
    )

    return jsonify({"contact": response.__dict__})

if __name__ == "__main__":
    app.run(host='127.0.0.1', port='5000', debug=True)