import json

class Reteta:
    def __init__(self, nume_reteta):
        self.retete = {}
        with open(nume_reteta) as f:
            data_reteta = json.load(f)
            for reteta_data in data_reteta["retete"]:
                self.retete[reteta_data["nume"]] = reteta_data

    def cautare_reteta(self, nume):
        if nume in self.retete:
            return self.retete[nume]
        else:
            return None

    def afisare_ingrediente(self, nume_reteta):
        if nume_reteta in self.retete:
            print(f"Ingrediente pentru rețeta '{nume_reteta}':")
            for ingredient in self.retete[nume_reteta]['ingrediente']:
                print(f"- {ingredient['nume']}: {ingredient['cantitate']}")
        else:
            print("Rețeta specificată nu există.")
