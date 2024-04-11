import json
from reteta import Reteta

class Meniu:
    def __init__(self, nume_meniu):
        self.sortimente = []
        with open(nume_meniu) as f:
            data_meniu = json.load(f)
            for sortiment_data in data_meniu["sortimente"]:
                self.sortimente.append(sortiment_data)

    def afisare_meniu(self):
        reteta = Reteta("reteta.json")  # Inițializez obiectul Reteta aici
        print("Meniu:")
        for sortiment in self.sortimente:
            print(f"\n{sortiment['nume']}:")
            for reteta_data in sortiment['retele']:
                nume_reteta = reteta_data['nume']
                reteta_info = reteta.cautare_reteta(nume_reteta)  # Caut rețeta în obiectul Reteta
#                print(f" - {nume_reteta} - {reteta_info['pret']} RON")
                print(f"   Ingrediente pentru rețeta '{nume_reteta}':")

                for ingredient in reteta_info['ingrediente']:
                    print(f"   - {ingredient['nume']}: {ingredient['cantitate']}")
                print(f"   Pret: {reteta_info['pret']}")
                print(f"   Valori nutritionale: {reteta_info['valori_nutritionale']['calorii']} calorii, {reteta_info['valori_nutritionale']['cantitate']} cantitate")
                # print(f"   Rating: {reteta_info['rating']['valoare']}/100 (Bazat pe {reteta_info['rating']['evaluari']} evaluări)")
                print(f"   Rating: {reteta_info['rating']['valoare']} (Bazat pe {reteta_info['rating']['evaluari']} evaluări)")

    def afisare_retele_categorie(self, categorie):
        print(f"Rețete din categoria '{categorie}':")
        for sortiment in self.sortimente:
            if sortiment['nume'] == categorie:
                for reteta in sortiment['retele']:
                    print(f"- {reteta['nume']}")
                print()
                return
        print("Categoria specificată nu există.")
