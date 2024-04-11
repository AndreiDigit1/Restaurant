import json

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

LIMIT_AGE = 18


@app.route('/menu_html')
def menu_html():
    response_menu = requests.get('http://127.0.0.1:5000/menu_route')
    data_menu = response_menu.json()

    menu_html = '<center><h2>Menu</h2></center><ul>'
    for category_data in data_menu:
        for category, items in category_data.items():
            for item in items:
                if category == 'dishes':
                    menu_html += f'<li>Dish: {item["name"]} - Price: {item["price"]} RON - Quantity: {item["quantity(g)"]}g - Nutritional Values: {item["nutritional_values(kcal)"]}kcal</li>'
                elif category == 'drinks':
                    menu_html += f'<li>Drink: {item["name"]} - Price: {item["price"]} RON - Quantity: {item["quantity(ml)"]}ml - Nutritional Values: {item["nutritional_values(kcal)"]}kcal - {"Alcohol" if item["isAlcohol"] else "Non-alcohol"}</li>'
    menu_html += '</ul>'

    return menu_html

@app.route('/')
def index():
    menu_html = requests.get('http://127.0.0.1:5000/menu_html').text
    response_reservations = requests.get('http://127.0.0.1:5000/reservations')
    data_reservations = response_reservations.json()

    return render_template('index.html', menu=menu_html, reservations_list=data_reservations)


@app.route('/createReservation')
def addReservation():
    response_tables = requests.get('http://127.0.0.1:5000/tables')
    data_tables = response_tables.json()
    return render_template('reservation.html', tables_data = data_tables)


@app.route('/users')
def users():
    all_clients = []
    reservations_response = requests.get('http://127.0.0.1:5000/reservations')
    reservations = reservations_response.json()

    for reservation in reservations:
        for client in reservation['clients']:
            client_info = {
                'id': client['id'],
                'firstname': client['firstname'],
                'lastname': client['lastname'],
                'age': client['age']
            }
            all_clients.append(client_info)

    return jsonify(all_clients)


@app.route('/order', methods=['POST'])
def order():
    global LIMIT_AGE
    reservations_response = requests.get('http://127.0.0.1:5000/reservations')
    reservations = reservations_response.json()

    menu_response = requests.get('http://127.0.0.1:5000/menu_route')
    menu_data = menu_response.json()

    orders_list = []

    for key in request.form:
        if key.startswith('order_'):
            parts = key.split('_')
            reservation_id = parts[1]
            client_id = parts[2]
            order = request.form[key]
            client_age =  request.form.get('age_' + reservation_id + '_' + client_id)
            items = [item.strip() for item in order.split(',')]

            valid_items_dishes = []
            valid_items_drinks = []
            for produs in items:
                for category_data in menu_data:
                    for category, items_data in category_data.items():
                        for item in items_data:
                            if item['name'].lower() == produs.lower():
                                if category == 'dishes' and item['quantity(g)'] > 0:
                                    valid_items_dishes.append(produs)
                                elif category == 'drinks' and item['quantity(ml)'] > 0:
                                     if not item['isAlcohol']:
                                         valid_items_drinks.append(produs)
                                     elif item['isAlcohol'] and int(client_age) >= int(LIMIT_AGE):
                                        valid_items_drinks.append(produs)
                                break

            valid_items = {'dishes': valid_items_dishes, 'drinks': valid_items_drinks}
            orders_list.append({'client_id': client_id, 'order': valid_items, 'reservation_id': reservation_id})

    list_order_client = []

    for order_info in orders_list:
        client_id = order_info['client_id']
        order_items = order_info['order']
        id_reservation = order_info['reservation_id']

        for reservation in reservations:
            if reservation['id'] == int(id_reservation):
                for client in reservation['clients']:
                    if client['id'] == int(client_id):
                        order_client = OrderClient(client_id, client['firstname'], client['lastname'], client['age'],
                                                   order_items)
                        print(order_client)
                        list_order_client.append(order_client)

    dict_list_order_client = []
    for order_client in list_order_client:
        client_dict = {
            'id': order_client.id,
            'firstname': order_client.firstname,
            'lastname': order_client.lastname,
            'age': order_client.age,
            'products': order_client.products
        }
        dict_list_order_client.append(client_dict)

    with open('orders.json', 'w') as file:
        json.dump(dict_list_order_client, file, indent=2)
    return jsonify(dict_list_order_client)


@app.route('/orders')
def orders():
    response = requests.post('http://127.0.0.1:5000/order')
    order_list = response.json()

    orders_data = []

    for order in order_list:
        order_info = {
            'id_order': order.id,
            'table_order': order.table,
            'clients': []
        }

        for client in order.clients:
            client_info = {
                'id': client.id,
                'firstname': client.firstname,
                'lastname': client.lastname,
                'age': client.age,
                'order': []
            }
            order_info['clients'].append(client_info)

        orders_data.append(order_info)

    serialized_orders_data = json.dumps(orders_data)

    return serialized_orders_data

@app.route('/restaurant-details')
def restaurant():
    restaurant_data = {
        'id': 1,
        'name': 'Bistro Gourmet',
        'address': '123 Main Street, Bucharest',
        'opening_hours': '11:00 AM',
        'closing_hours': '10:00 PM',
        'num_tables': 20,
        'num_seats': 120
    }
    return jsonify(restaurant_data)

@app.route('/reservations')
def reservations():
    reservations_data = [
        {'id': 1, 'table': 10, 'clients': [
            {'id': 101, 'firstname': 'John', 'lastname': 'Doe', 'age': 16},
            {'id': 102, 'firstname': 'Jane', 'lastname': 'Smith', 'age': 28}
        ]},
        {'id': 2, 'table': 11, 'clients': [
            {'id': 103, 'firstname': 'Alice', 'lastname': 'Johnson', 'age': 42},
            {'id': 104, 'firstname': 'Bob', 'lastname': 'Brown', 'age': 30}
        ]}
    ]
    return jsonify(reservations_data)


@app.route('/menu_route')
def menu_route():
    menu_route_data = [
        {'dishes': [
            {'name': 'Pui', 'price': 10, 'quantity(g)': 100, 'nutritional_values(kcal)': 200},
            {'name': 'Orez', 'price': 16, 'quantity(g)': 200, 'nutritional_values(kcal)': 400}
        ]},
        {'drinks': [
            {'name': 'Cola', 'price': 20, 'quantity(ml)': 300, 'nutritional_values(kcal)': 80, 'isAlcohol': False},
            {'name': 'Vin', 'price': 30, 'quantity(ml)': 150, 'nutritional_values(kcal)': 100, 'isAlcohol': True}
        ]}
    ]
    return jsonify(menu_route_data)


@app.route('/tables')
def tables():
    tables_data = [
        {'table': 10, 'state': True, 'number_seats': 5, 'number_seats_available': 2},
        {'table': 11, 'state': True, 'number_seats': 5, 'number_seats_available': 3},
        {'table': 12, 'state': False, 'number_seats': 5, 'number_seats_available': 5},
        {'table': 13, 'state': True, 'number_seats': 5, 'number_seats_available': 1},
        {'table': 14, 'state': True, 'number_seats': 5, 'number_seats_available': 4},
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
            'id': self.id,
            'table': self.table,
            'clients': [client.to_json() for client in self.clients]
        }


class OrderClient(Client):
    def __init__(self, client_id, firstname, lastname, age, list_of_products_desired):
        super().__init__(client_id, firstname, lastname, age)
        self.products = list_of_products_desired

    def __str__(self):
        return f"Client: ID: {self.id}, Name: {self.firstname} {self.lastname}, Age: {self.age}, Products: {self.products}"

    def to_json(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'age': self.age,
            'products': self.products
        }

class Restaurant:
    def __init__(self, name, addres, open_hour, close_hour, nr_of_tables, nr_of_seats):
        self.name = name
        self.address = addres
        self.open_hour = open_hour
        self.close_hour = close_hour
        self.nr_of_tables = nr_of_tables
        self.nr_of_seats = nr_of_seats


if __name__ == '__main__':
    app.run(debug=True)