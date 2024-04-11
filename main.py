from flask import Flask, jsonify, render_template,request
from client import Client
from datetime import datetime, time

app = Flask(__name__)
clients = []
available_seats = 5  # Global variable for available seats

# Define the opening and closing times of the restaurant
opening_time = time(9, 0)  # Assuming the restaurant opens at 9:00 AM
closing_time = time(21, 0)  # Assuming the restaurant closes at 9:00 PM

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_client', methods =["GET", "POST"])
def add_clients():
    global available_seats

    if request.method == "POST":
        if available_seats > 0:
            # Getting input from the HTML form
            name = request.form.get("fname")
            surname = request.form.get("surname")
            age = request.form.get("age")
            phone = request.form.get("phone")
            email = request.form.get("email")

            # Create a new Client object with form data
            client = Client(name, surname, age, email, phone)

            # Append the client to the clients list
            clients.append(client)

            #decrement available seats once the client has been added
            available_seats -= 1
            # Save JSON data locally
            Client.save_clients_to_file(clients)

            # Render a template with success message and buttons
            return render_template("client_added.html",available_seats=available_seats)
        else:
            return "No seats available. Cannot add client."
    return render_template("add_client.html")

@app.route('/check_status/<int:client_id>')
def check_status(client_id):
    # Find the client by client_id
    client = next((client for client in clients if client.id == client_id), None)
    if client:
        current_time = datetime.now().time()
        if opening_time <= current_time <= closing_time:
            status = "open"
        else:
            status = "closed"
        return render_template('status.html', status=status, client=client)
    else:
        return "Client not found"

@app.route('/check_all_status')
def check_all_status():
    current_time = datetime.now().time()
    status_list = []
    for client in clients:
        if opening_time <= current_time <= closing_time:
            status = "open"
        else:
            status = "closed"
        status_list.append({'client': client, 'status': status})
    return render_template('all_status.html', status_list=status_list)

@app.route('/search_clients', methods=['GET'])
def search_clients():
    search_query = request.args.get('search_name')

    # Search for clients by name
    search_results = [client for client in clients if client.name == search_query]

    # Assuming clients have unique names, so there should be only one matching client
    if search_results:
        client_id = search_results[0].id  # Get the ID of the matching client
        # Render search_clients.html with search results and client ID
        return render_template('search_clients.html', search_results=search_results, search_query=search_query, client_id=client_id)
    else:
        # No matching clients found
        return render_template('search_clients.html', search_results=[], search_query=search_query, client_id=None)

@app.route('/client-page')
def client_page():
    client_data = [client.to_dict() for client in clients]
    return jsonify(client_data)


if __name__ == '__main__':
    app.run(debug=True)
