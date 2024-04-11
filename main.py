from meniu import Meniu
from reteta import Reteta

def main():
    meniu = Meniu("meniu.json")
    meniu.afisare_meniu()

if __name__ == "__main__":
    main()
