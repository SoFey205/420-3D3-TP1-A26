from observateurs.observateur import Observateur


def formater_prix(prix, ouverture):
    variation = prix - ouverture

    if variation >= 0:
        symbole = "▲"
        couleur = "green"
    else:
        symbole = "▼"
        couleur = "red"

    variation_pourcentage = (variation / ouverture) * 100

    texte = f"{prix:.2f} $ {symbole} {abs(variation_pourcentage):.2f}%"

    return texte, couleur


class Prix(Observateur):

    def __init__(self, labels_prix):
        self.labels_prix = labels_prix

    def actualiser(self, sujet):
        donnees = sujet.get_donnees()
        prix_actuels = donnees["prix_actuels"]

        for ticker, (prix, ouverture) in prix_actuels.items():
            texte, couleur = formater_prix(prix, ouverture)

            self.labels_prix[ticker].config(
                text=texte,
                fg=couleur
            )