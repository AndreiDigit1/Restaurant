import json
class Client:
    last_id = 0  # Class variable to store the last assigned ID
    def __init__(self, name, surname, age, email, phone):
        self.id = Client.generate_id()  # Assign the new ID
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
            "id":self.id,
            "name": self.name,
            "surname": self.surname,
            "age": self.age,
            "email": self.email,
            "phone": self.phone
        }

    @staticmethod
    def save_clients_to_file(clients):
        with open('clients.json', 'w') as f:
            json.dump([client.to_dict() for client in clients], f,  indent=2)