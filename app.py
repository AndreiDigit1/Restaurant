from flask import Flask, render_template, jsonify, request, flash
import json


app = Flask(__name__)
app.secret_key = "cheie_secreta_pentru_mesaje_flash"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/load_menu', methods=['GET'])
def load_menu():
    try:

        with open('meniu.json', 'r') as file:
            menu_data = json.load(file)
        return jsonify(menu_data)
    except Exception as e:

        flash('Eroare la încărcarea meniului: {}'.format(str(e)))
        return jsonify([])

@app.route('/load_recipe', methods=['GET'])
def load_recipe():
    try:

        with open('reteta.json', 'r') as file:
            menu_data = json.load(file)
        return jsonify(menu_data)
    except Exception as e:

        flash('Eroare la încărcarea meniului: {}'.format(str(e)))
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=True)
