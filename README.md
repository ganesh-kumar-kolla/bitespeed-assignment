# Contact Reconciliation Service

This project implements a contact reconciliation service using Flask and SQLite. The service allows you to identify and link contacts based on their email addresses and phone numbers, ensuring that multiple entries referring to the same person are properly consolidated.


## Endpoint 

This application is hosted on render.com at https://bitespeed-assignment-2lhh.onrender.com/. 
The identify endpoint is available at https://bitespeed-assignment-2lhh.onrender.com/identify
## Features

- Add new contacts with email and/or phone number.
- Link new contacts to existing ones if they share an email or phone number.
- Handle scenarios where a primary contact turns into a secondary contact.


## Requirements

- Python 3.7+
- Flask
- SQLite


## Setup

1. **Clone the repository:**

    Open Command Prompt and run:
    ```cmd
    git clone https://github.com/ganesh-kumar-kolla/bitespeed-assignment.git
    cd bitespeed-assignment
    ```

2. **Create a virtual environment and activate it:**

    ```cmd
    python -m venv venv
    venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```cmd
    pip install -r requirements.txt
    ```

4. **Initialize the database :**

    ```cmd
    python db_init.py
    ```

5. **Run the application:**

    ```cmd
    python app.py
    ```

    The application will start running at `http://127.0.0.1:5000/`.

## API Usage

### Identify Contact

**Endpoint:** `/identify`  
**Method:** `POST`  
**Description:** Identifies and links contacts based on email and phone number.

**Request Body:**

```json
{
    "email": "example@domain.com",
    "phoneNumber": "1234567890"
}
```