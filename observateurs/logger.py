from datetime import datetime
from observateurs.observateur import Observateur


class Logger(Observateur):

    def actualiser(self, sujet):
        donnees = sujet.get_donnees()
        prix_actuels = donnees["prix_actuels"]

        horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("./portfolio.csv", "a") as f:
            for ticker, (prix, ouverture) in prix_actuels.items():
                f.write(
                    f"{horodatage},{ticker},{prix:.2f},{ouverture:.2f}\n"
                )