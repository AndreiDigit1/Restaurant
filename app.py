import json
import random
import re

import requests
from flask import Flask, jsonify, render_template, request, redirect, url_for
from client import Client
from datetime import datetime, time

opening_time = time(9, 0)
closing_time = time(21, 0)

app = Flask(__name__)
#To preserve order of inserted keys
app.json.sort_keys = False

LIMIT_AGE = 18

reservations_data = []
clients = []
available_seats = 5


@app.route("/")
def index():
    response_menu = requests.get("http://127.0.0.1:5000/menu_route")
    data_menu = response_menu.json()

    response_reservations = requests.get("http://127.0.0.1:5000/reservations")
    data_reservations = response_reservations.json()

    return render_template(
        # trimitem in index.html valorile din rutele pe care le cream in codul python
        # trimitem meniul prin variabila data_menu si rezervarile prin reservations_list pe care le vom accesa in index.html prin % for %
        "index.html", data_menu=data_menu, reservations_list=data_reservations
    )
@app.route("/menu_show")
def show_menu():
    try:
        with open("menu.json", "r") as file:
            menu_data = json.load(file)
    except FileNotFoundError:
        return jsonify({"error": "Menu data not found"}), 404
    except json.decoder.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in menu file"}), 500

    return render_template('menu.html', menu_data=menu_data)

@app.route("/index_show")
def show_index():
    try:
        with open("menu.json", "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        return jsonify({"error": "Menu data not found"}), 404
    except json.decoder.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in menu file"}), 500

    return render_template('index.html', data=data)

@app.route('/ratings')
def ratings():
    response_menu = requests.get('http://127.0.0.1:5000/menu_route')
    menu_data = response_menu.json()

    return render_template('ratings.html', menu=menu_data)

@app.route("/createReservation", methods=["POST", "GET"])
def addReservation():
    if request.method == "POST":
        current_date = datetime.now().strftime("%Y-%m-%d")
        number_clients = request.form.get('number_clients')
        reservation_time = request.form.get('reservation_time')
        if reservation_time < current_date:
            return "The date must be greater than the current date!"
        if int(number_clients) > 5:
            return "Maxim five clients for a reservation!"
        print(number_clients)
        print(reservation_time)
        if number_clients is not None:
            number_clients = int(number_clients)
        with open("tables_data_multiple_days.json", "r") as file:
            tables_data_multiple_days = json.load(file)

        data_tables = None
        if reservation_time in tables_data_multiple_days:
            data_tables = tables_data_multiple_days[reservation_time]
        else:
            default_data = [
                {"table": 10, "state": True, "number_seats": 5, "number_seats_available": 5},
                {"table": 11, "state": True, "number_seats": 5, "number_seats_available": random.randint(1,5)},
                {"table": 12, "state": True, "number_seats": 5, "number_seats_available": random.randint(1,5)},
                {"table": 13, "state": True, "number_seats": 5, "number_seats_available": 5},
                {"table": 14, "state": True, "number_seats": 5, "number_seats_available": 5},
            ]
            tables_data_multiple_days[reservation_time] = default_data
            data_tables = default_data

            with open("tables_data_multiple_days.json", "w") as file:
                json.dump(tables_data_multiple_days, file, indent=4)

        return render_template("reservation.html", number_clients=number_clients,reservation_time=reservation_time, tables_data=data_tables)
    elif request.method == "GET":
        return render_template("reservation.html")


@app.route("/users")
def users():
    all_clients = []
    reservations_response = requests.get("http://127.0.0.1:5000/reservations")
    reservations = reservations_response.json()

    for reservation in reservations:
        for client in reservation["clients"]:
            client_info = {
                "id": client["id"],
                "name": client["name"],
                "surname": client["surname"],
                "age": client["age"],
                "email": client["email"],
                "phone": client["phone"]
            }
            all_clients.append(client_info)

    return jsonify(all_clients)

@app.route('/menu_names', methods=['POST'])
def get_menu_names():
    data = request.json
    item_names = data.get('itemNames', [])

    return jsonify(itemNames=item_names)

@app.route("/menu_show/add_item", methods=["POST"])
def add_item():
    item_data = request.json

    if "name" not in item_data or "recipe" not in item_data or "price" not in item_data or "type" not in item_data:
        return jsonify({"error": "Incomplete data"}), 400

    item_type = item_data["type"]
    item_name = item_data["name"]
    item_isAlcohol = item_data["isAlcohol"]
    item_price = item_data["price"]
    item_recipe = item_data["recipe"]

    ingredients = item_recipe.get("ingredients", [])
    quantities = item_recipe.get("quantities", [])

    if len(ingredients) != len(quantities):
        return jsonify({"error": "Invalid recipe data"}), 400

    recipe_list = []
    for ingredient, quantity in zip(ingredients, quantities):
        recipe_list.append({"ingredient": ingredient, "quantity": quantity})

    recipe = {
        "recipe": recipe_list
    }

    try:
        with open("menu.json", "r") as file:
            menu_data = json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        menu_data = {"drinks": [], "dishes": []}

    # Verificăm tipul elementului și adăugăm în lista corespunzătoare
    if item_type == "drinks":
        menu_data["drinks"].append({
            "name": item_name,
            "price": item_price,
            "isAlcohol": item_isAlcohol,
            **recipe
        })
    elif item_type == "dishes":
        menu_data["dishes"].append({
            "name": item_name,
            "price": item_price,
            "isAlcohol": item_isAlcohol,
            **recipe
        })
    else:
        return jsonify({"error": "Invalid item type"}), 400

    with open("menu.json", "w") as file:
        json.dump(menu_data, file, indent=2)

    return jsonify({"message": "Item added successfully"}), 201


@app.route("/add_ingredients", methods=["POST"])
def ingredients():
    # Primește datele JSON din corpul cererii
    ingredient_data = request.json

    # Verifică dacă sunt furnizate ambele câmpuri necesare
    if "ingredient_name" not in ingredient_data or "quantity" not in ingredient_data:
        return jsonify({"error": "Ingredient name and quantity are required"}), 400

    # Extrage informațiile despre ingredient
    ingredient_name = ingredient_data["ingredient_name"]
    quantity = ingredient_data["quantity"]

    # Încarcă datele actuale din fișierul JSON, dacă există
    try:
        with open("ingredients.json", "r") as file:
            ingredients = json.load(file)
    except FileNotFoundError:
        ingredients = []

    # Adaugă ingredientul nou la lista de ingrediente
    ingredients.append({"ingredient_name": ingredient_name, "quantity": quantity})

    # Salvează lista actualizată de ingrediente înapoi în fișierul JSON
    with open("ingredients.json", "w") as file:
        json.dump(ingredients, file, indent=2)

    # Răspunde cu un mesaj de succes
    return jsonify({"message": "Ingredient added successfully"}), 201



@app.route("/order", methods=["POST", "GET"])
def order():
    global LIMIT_AGE
    reservations_response = requests.get("http://127.0.0.1:5000/reservations")
    reservations = reservations_response.json()

    with open("menu.json", "r") as menu_file:
        menu_data = json.load(menu_file)

    orders_list = []  # Inițializăm lista în afara buclei

    errors = []
    for key in request.form:
        if key.startswith("order_"):
            parts = key.split("_")
            reservation_id = parts[1]
            client_id = parts[2]
            order = request.form[key]
            client_age = request.form.get("age_" + reservation_id + "_" + client_id)

            if request.method == 'POST':
                selected_items = request.form.getlist('menu_items[]')

            ratings = request.form.get('rating_' + reservation_id + '_' + client_id)

            valid_items_dishes = []
            valid_items_drinks = []
            for product in selected_items:
                found = False
                for category, items_data in menu_data.items():
                    for item in items_data:
                        if item['name'].lower() == product.lower():
                            found = True
                            if category == 'dishes' and item['quantity(g)'] > 0:
                                valid_items_dishes.append({
                                    'name': product,
                                    'rating': float(ratings) if ratings else None
                                })
                            elif category == 'drinks' and item['quantity(ml)'] > 0:
                                if not item['isAlcohol']:
                                    valid_items_drinks.append({
                                        'name': product,
                                        'rating': float(ratings) if ratings else None
                                    })
                                elif item['isAlcohol'] and int(client_age) >= int(LIMIT_AGE):
                                    valid_items_drinks.append({
                                        'name': product,
                                        'rating': float(ratings) if ratings else None
                                    })
                            break
                if not found:
                    errors.append(f"Invalid order: {product}")

            valid_items = {'dishes': valid_items_dishes, 'drinks': valid_items_drinks}
            orders_list.append({'client_id': client_id, 'order': valid_items, 'reservation_id': reservation_id})

    if errors:
        error_message = ', '.join(errors)
        return render_template('order_error.html', error_message=error_message), 400

    list_order_client = []

    for order_info in orders_list:
        client_id = order_info["client_id"]
        order_items = order_info["order"]
        id_reservation = order_info["reservation_id"]

        for reservation in reservations:
            if reservation["id"] == int(id_reservation):
                for client in reservation["clients"]:
                    if client["id"] == int(client_id):
                        order_client = OrderClient(
                            client["id"],
                            client["name"],
                            client["surname"],
                            client["age"],
                            client["email"],
                            client["phone"],
                            order_items,
                        )
                        list_order_client.append(order_client)

    dict_list_order_client = []
    for order_client in list_order_client:
        client_dict = {
            "id": order_client.id,
            "name": order_client.name,
            "surname": order_client.surname,
            "age": order_client.age,
            "email": order_client.email,
            "phone": order_client.phone,
            "products": order_client.products,
        }
        dict_list_order_client.append(client_dict)

    with open("orders.json", "w") as file:
        json.dump(dict_list_order_client, file, indent=2)

    return jsonify(dict_list_order_client)



@app.route("/restaurant-details")
def restaurant():
    restaurant_data = {
        "id": 1,
        "name": "Bistro Gourmet",
        "address": "123 Main Street, Bucharest",
        "opening_hours": "11:00 AM",
        "closing_hours": "10:00 PM",
        "num_tables": 20,
        "num_seats": 120,
    }
    return jsonify(restaurant_data)


@app.route("/reservations")
def reservations():
    with open('reservations.json', 'r') as file:
        reservations_data = json.load(file)
    return jsonify(reservations_data)


@app.route("/ingredients")
def show_ingredients():
    try:
        with open("ingredients.json", "r") as file:
            ingredients_data = json.load(file)
    except FileNotFoundError:
        return jsonify({"error": "Ingredient data not found"}), 404
    except json.decoder.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in file"}), 500

    return jsonify(ingredients_data)

@app.route("/menu_route")
def menu_route():
    # menu_route_data = {
    #     "dishes": [
    #         {
    #             "name": "Pui",
    #             "price": 10,
    #             "quantity(g)": 100,
    #             "nutritional_values(kcal)": 200,
    #             'ratings': 4.5,
    #         },
    #         {
    #             "name": "Orez",
    #             "price": 16,
    #             "quantity(g)": 200,
    #             "nutritional_values(kcal)": 400,
    #             'ratings': 3.8,
    #         },
    #     ],
    #     "drinks": [
    #         {
    #             "name": "Cola",
    #             "price": 20,
    #             "quantity(ml)": 300,
    #             "nutritional_values(kcal)": 80,
    #             "isAlcohol": False,
    #             'ratings': 4.2,
    #         },
    #         {
    #             "name": "Vin",
    #             "price": 30,
    #             "quantity(ml)": 150,
    #             "nutritional_values(kcal)": 100,
    #             "isAlcohol": True,
    #             'ratings': 4.8,
    #         },
    #     ]
    # }

    try:
        with open("menu.json", "r") as file:
            menu_route_data = json.load(file)
    except FileNotFoundError:
        return jsonify({"error": "Menu data not found"}), 404
    except json.decoder.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format in menu file"}), 500


    return jsonify(menu_route_data)



@app.route("/tables")
def tables():
    with open("tables_data.json", "r") as file:
        tables_data = json.load(file)
    return jsonify(tables_data)

class Client:
    last_id = 0
    def __init__(self, name, surname, age, email, phone):
        self.id = Client.generate_id()
        self.name = name
        self.surname = surname
        self.age = age
        self.email = email
        self.phone = phone

    @staticmethod
    def generate_id():
        Client.last_id += 1
        return Client.last_id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "age": self.age,
            "email": self.email,
            "phone": self.phone
        }

    @staticmethod
    def save_clients_to_file(clients):
        with open('clients.json', 'w') as f:
            json.dump([client.to_dict() for client in clients], f)

class Reservation:
    reservation_id = 100

    def __init__(self, number_of_table, list_client):
        self.id = Reservation.reservation_id
        Reservation.reservation_id += 1
        self.numberTable = number_of_table
        self.list_client = list_client


class Order:
    current_id = 1

    def __init__(self, table_number, list_order_clients):
        self.id = Order.current_id
        Order.current_id += 1
        self.table = table_number
        self.clients = list_order_clients

    def to_json(self):
        return {
            "id": self.id,
            "table": self.table,
            "clients": [client.to_json() for client in self.clients],
        }


class OrderClient(Client):
    def __init__(self, client_id, name, surname, age, email, phone, list_of_products_desired):
        super().__init__(name, surname, age, email, phone)
        self.products = list_of_products_desired

    def __str__(self):
        return f"Client: ID: {self.id}, Name: {self.name} , Surname: {self.surname}, Age: {self.age}, Email: {self.email}, Phone: {self.phone}, Products: {self.products}"

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "surname": self.surname,
            "age": self.age,
            "email": self.email,
            "phone": self.phone,
            "products": self.products,
        }


class Restaurant:
    def __init__(self, name, addres, open_hour, close_hour, nr_of_tables, nr_of_seats):
        self.name = name
        self.address = addres
        self.open_hour = open_hour
        self.close_hour = close_hour
        self.nr_of_tables = nr_of_tables
        self.nr_of_seats = nr_of_seats

class Ingredients:
    def __init__(self, ingredient_name, quantity):
        self.ingredient_name = ingredient_name
        self.quantity = quantity

        
all_clients = []

@app.route('/add_client', methods=["GET", "POST"])
def add_clients():
    global all_clients

    if request.method == "POST":
        name = request.form.get("fname")
        surname = request.form.get("surname")
        age = request.form.get("age")
        phone = request.form.get("phone")
        email = request.form.get("email")

        client = Client(name, surname, age, email, phone)

        all_clients.append(client)

        return redirect(url_for("add_clients"))
    return render_template("add_client.html")

reservation_details = []


@app.route("/add_reservation", methods=["POST"])
def add_reservation():
    validation_errors = []
    number_clients = request.form['number_clients']
    reservation_time = request.form['reservation_time']
    id = request.form.get("number_table")
    number_table = request.form.get("number_table")
    if(int(number_table) < 10 or int(number_table) > 14):
        return "The number table is invalid!"

    with open("tables_data_multiple_days.json", "r") as file:
        tables_data_multiple_days = json.load(file)

    print(reservation_time)

    if reservation_time in tables_data_multiple_days:
        tables_data = tables_data_multiple_days[reservation_time]

        for table in tables_data:
            if table["table"] == int(number_table) and table["state"] == False:
                return (f"The table {int(number_table)} is full!")
            if table["table"] == int(number_table) and table["state"] == True:
                if int(table["number_seats_available"]) != int(table["number_seats"]):
                    number_taken_seats = int(table["number_seats"]) - int(table["number_seats_available"])
                    return (f"The table {int(number_table)} is already reserved for {int(number_taken_seats)} people!")


    if reservation_time in tables_data_multiple_days:
        tables_data = tables_data_multiple_days[reservation_time]

        for table in tables_data:
            if table["table"] == int(number_table) and table["state"] == True:
                if int(table["number_seats_available"]) >= int(number_clients):
                    table["number_seats_available"] = int(table["number_seats_available"]) - int(number_clients)
                    if int(table["number_seats_available"]) == 0:
                        table["state"] = False
                    break
                else:
                    return jsonify({"error": "Not enough available seats for the chosen table."})


        with open("tables_data_multiple_days.json", "w") as file:
            json.dump(tables_data_multiple_days, file, indent=4)


    print(request.form)
    clients = []

    for i in range(int(number_clients)):
        name = request.form.get(f"name{i}")
        surname = request.form.get(f"surname{i}")
        age = request.form.get(f"age{i}")
        phone = request.form.get(f"phone{i}")

        if not validate_name(name):
            validation_errors.append("The name must contain only letters!")
        if not validate_name(surname):
            validation_errors.append("The surname must contain only letters!")
        if not validate_numbers(age) or not (15 <= int(age) <= 85):
            validation_errors.append("The age must contain only numbers or be in the interval [15-85]!")
        if not validate_numbers(phone):
            validation_errors.append("Phone number must contain only numbers!")

        client = {
            "id": int(request.form.get(f"id{i}")),
            "name": request.form.get(f"name{i}"),
            "surname": request.form.get(f"surname{i}"),
            "age": int(request.form.get(f"age{i}")),
            "phone": request.form.get(f"phone{i}"),
            "email": request.form.get(f"email{i}")
        }
        clients.append(client)

    reservation = {
        "id": int(id),
        "table": int(number_table),
        "number_clients": int(number_clients),
        "reservation_time": reservation_time,
        "clients": clients
    }

    reservation_details.append(reservation)

    with open("reservations.json", "w") as file:
        json.dump(reservation_details, file, indent=2)

    if validation_errors:
        return render_template('validation_errors.html', errors=validation_errors)

    return render_template('interface_reservation.html', reservation=reservation)


def validate_name(name):
    regex = "^[a-zA-Z ]+$"
    return bool(re.match(regex, name))

def validate_numbers(age):
    regex = "^[0-9]+$"
    return bool(re.match(regex, age))

@app.route("/show_reservations", methods=["GET"])
def show_reservations():
    return jsonify(reservation_details)


@app.route('/check_status/<int:client_id>')
def check_status(client_id):
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

    search_results = []
    reservations_response = requests.get("http://127.0.0.1:5000/reservations")
    reservations = reservations_response.json()

    for reservation in reservations:
        for client in reservation["clients"]:
            if client["name"] == search_query:
                search_results.append(client)


    # Search for clients by name
    # search_results = [client for client in clients if client.name == search_query]

    if search_results:
        client_id = search_results[0]["id"]
        return render_template('search_clients.html', search_results=search_results, search_query=search_query, client_id=client_id)
    else:
        return render_template('search_clients.html', search_results=[], search_query=search_query, client_id=None)

@app.route('/client-page')
def client_page():
    client_data = [client.to_dict() for client in clients]
    return jsonify(client_data)


@app.route("/payment_note_client", methods=["GET"])
def payment_note_on_the_client():

    menu_response = requests.get("http://127.0.0.1:5000/menu_route")
    menu_route_data = menu_response.json()

    try:
        with open("orders.json", "r") as file:
            orders_data = json.load(file)

        payment_details = {}

        for order in orders_data:
            total_plata = 0
            for category, items in menu_route_data.items():
                for item in items:
                    if category == 'dishes':
                        for dish_order in order['products']['dishes']:
                            if dish_order['name'].lower() == item['name'].lower():
                                total_plata += item['price']
                    elif category == 'drinks':
                        for drink_order in order['products']['drinks']:
                            if drink_order['name'].lower() == item['name'].lower():
                                total_plata += item['price']

            payment_details[order['id']] = total_plata
            print(f"Totalul de plata pentru clientul {order['id']} este {total_plata}")

        payment_notes = [{"ID client": client_id, "Payment_client": payment} for client_id, payment in payment_details.items()]

        return jsonify(payment_notes)
    except FileNotFoundError:
        return jsonify({"message": "No orders found"}), 404


@app.route("/payment_note_order", methods=["GET"])
def payment_note_on_the_order():
    total_plata = 0
    number_clients = 0

    payment_details = []
    menu_response = requests.get("http://127.0.0.1:5000/menu_route")
    menu_route_data = menu_response.json()

    try:
        with open("orders.json", "r") as file:
            orders_data = json.load(file)

        for order in orders_data:
            number_clients += 1
            for category, items in menu_route_data.items():
                for item in items:
                    if category == 'dishes':
                        for dish_order in order['products']['dishes']:
                            if dish_order['name'].lower() == item['name'].lower():
                                print("Nume mancare:", item['name'])
                                print("Pret mancare:", item['price'])
                                total_plata += item['price']
                    elif category == 'drinks':
                        for drink_order in order['products']['drinks']:
                            if drink_order['name'].lower() == item['name'].lower():
                                print("Nume bautura:", item['name'])
                                print("Pret bautura:", item['price'])
                                total_plata += item['price']

        payment_details.append({"clients_number": number_clients, "total_payment": total_plata})
        total_message = f"Totalul de plata pentru cei {number_clients} clienti este {total_plata}"
        print(total_message)

        return jsonify(payment_details)

    except FileNotFoundError:
        return jsonify({"message": "No orders found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
