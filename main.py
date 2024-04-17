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
            num_reservations = int(request.form.get("num_reservations"))
            # Create a new Client object with form data
            client = Client(name, surname, age, email, phone,num_reservations)

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
    search_name = request.args.get('search_name')
    search_reservations = request.args.get('search_reservations')
    search_phone = request.args.get('search_phone')

    if search_name:
        # Search for clients by name
        search_results = [client for client in clients if client.name == search_name]
    elif search_reservations:
        # Convert search_reservations to an integer
        search_reservations = int(search_reservations)
        # Search for clients by number of reservations
        search_results = [client for client in clients if client.num_reservations == search_reservations]
    elif search_phone:
        # Search for clients by phone number
        search_results= [client for client in clients if client.phone == search_phone]
    else:
        # No search criteria provided, return all clients
        search_results = clients

    # Render the search results template
    return render_template('search_clients.html', search_results=search_results)


# Client page route (to get all clients' data)
@app.route('/client-page')
def client_page():
    return render_template('client_page.html', clients=clients)

@app.route('/api/delete_client/<int:client_id>', methods=['DELETE'])
def delete_client_api(client_id):
    global available_seats

    client = next((client for client in clients if client.id == client_id), None)
    if client:
        available_seats += 1
        clients.remove(client)
        Client.save_clients_to_file(clients)  # Update the JSON file
        return jsonify({"message": "Client deleted successfully."}), 200
    else:
        return jsonify({"error": "Client not found."}), 404

@app.route('/api/update_client/<int:client_id>', methods=['PUT'])
def update_client_api(client_id):
    data = request.json  # Get JSON data from the request body
    client = next((client for client in clients if client.id == client_id), None)
    if client:
        # Update client attributes
        if 'name' in data:
            client.name = data['name']
        if 'surname' in data:
            client.surname = data['surname']
        if 'age' in data:
            client.age = data['age']
        if 'email' in data:
            client.email = data['email']
        if 'phone' in data:
            client.phone = data['phone']

        # Save updated client list to file
        Client.save_clients_to_file(clients)

        return jsonify({"message": "Client updated successfully."}), 200
    else:
        return jsonify({"error": "Client not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)
