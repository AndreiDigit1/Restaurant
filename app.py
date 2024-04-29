import json

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
#To preserve order of inserted keys
app.json.sort_keys = False

LIMIT_AGE = 18


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

@app.route('/ratings')
def ratings():
    response_menu = requests.get('http://127.0.0.1:5000/menu_route')
    menu_data = response_menu.json()

    return render_template('ratings.html', menu=menu_data)

@app.route("/createReservation")
def addReservation():
    response_tables = requests.get("http://127.0.0.1:5000/tables")
    data_tables = response_tables.json()
    return render_template("reservation.html", tables_data=data_tables)


@app.route("/users")
def users():
    all_clients = []
    reservations_response = requests.get("http://127.0.0.1:5000/reservations")
    reservations = reservations_response.json()

    for reservation in reservations:
        for client in reservation["clients"]:
            client_info = {
                "id": client["id"],
                "firstname": client["firstname"],
                "lastname": client["lastname"],
                "age": client["age"],
            }
            all_clients.append(client_info)

    return jsonify(all_clients)

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

@app.route("/order", methods=["POST"])
def order():
    global LIMIT_AGE
    reservations_response = requests.get("http://127.0.0.1:5000/reservations")
    reservations = reservations_response.json()

    menu_response = requests.get("http://127.0.0.1:5000/menu_route")
    menu_data = menu_response.json()

    orders_list = []
    errors = []
    # accesam form-ul din index.html: <form method="post" action="/order">
    for key in request.form:
        if key.startswith("order_"):
            parts = key.split("_")
            reservation_id = parts[1]
            client_id = parts[2]
            order = request.form[key]
            client_age = request.form.get("age_" + reservation_id + "_" + client_id)
            items = [item.strip() for item in order.split(",")]

            ratings = request.form.get('rating_' + reservation_id + '_' + client_id)

            valid_items_dishes = []
            valid_items_drinks = []
            for product in items:
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
                            client_id,
                            client["firstname"],
                            client["lastname"],
                            client["age"],
                            order_items,
                        )
                        list_order_client.append(order_client)

    dict_list_order_client = []
    for order_client in list_order_client:
        client_dict = {
            "id": order_client.id,
            "firstname": order_client.firstname,
            "lastname": order_client.lastname,
            "age": order_client.age,
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
    reservations_data = [
        {
            "id": 1,
            "table": 10,
            "clients": [
                {"id": 101, "firstname": "John", "lastname": "Doe", "age": 16},
                {"id": 102, "firstname": "Jane", "lastname": "Smith", "age": 28},
            ],
        },
        {
            "id": 2,
            "table": 11,
            "clients": [
                {"id": 103, "firstname": "Alice", "lastname": "Johnson", "age": 42},
                {"id": 104, "firstname": "Bob", "lastname": "Brown", "age": 30},
            ],
        },
    ]
    return jsonify(reservations_data)


@app.route("/menu_route")
def menu_route():
    menu_route_data = {
        "dishes": [
            {
                "name": "Pui",
                "price": 10,
                "quantity(g)": 100,
                "nutritional_values(kcal)": 200,
                'ratings': 4.5,
            },
            {
                "name": "Orez",
                "price": 16,
                "quantity(g)": 200,
                "nutritional_values(kcal)": 400,
                'ratings': 3.8,
            },
        ],
        "drinks": [
            {
                "name": "Cola",
                "price": 20,
                "quantity(ml)": 300,
                "nutritional_values(kcal)": 80,
                "isAlcohol": False,
                'ratings': 4.2,
            },
            {
                "name": "Vin",
                "price": 30,
                "quantity(ml)": 150,
                "nutritional_values(kcal)": 100,
                "isAlcohol": True,
                'ratings': 4.8,
            },
        ]
    }

    return jsonify(menu_route_data)



@app.route("/tables")
def tables():
    tables_data = [
        {"table": 10, "state": True, "number_seats": 5, "number_seats_available": 2},
        {"table": 11, "state": True, "number_seats": 5, "number_seats_available": 3},
        {"table": 12, "state": False, "number_seats": 5, "number_seats_available": 5},
        {"table": 13, "state": True, "number_seats": 5, "number_seats_available": 1},
        {"table": 14, "state": True, "number_seats": 5, "number_seats_available": 4},
    ]
    return jsonify(tables_data)


class Client:
    def __init__(self, client_id, firstname, lastname, age):
        self.id = client_id
        self.firstname = firstname
        self.lastname = lastname
        self.age = age


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
    def __init__(self, client_id, firstname, lastname, age, list_of_products_desired):
        super().__init__(client_id, firstname, lastname, age)
        self.products = list_of_products_desired

    def __str__(self):
        return f"Client: ID: {self.id}, Name: {self.firstname} {self.lastname}, Age: {self.age}, Products: {self.products}"

    def to_json(self):
        return {
            "id": self.id,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "age": self.age,
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

if __name__ == "__main__":
    app.run(debug=True)
