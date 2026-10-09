from observateurs.observateur import Observateur


class Resume(Observateur):

    def __init__(self, label_valeur, label_variation):
        self.label_valeur = label_valeur
        self.label_variation = label_variation

    def actualiser(self, sujet):
        donnees = sujet.get_donnees()

        titres = donnees["titres"]
        prix_actuels = donnees["prix_actuels"]

        valeur_totale = 0
        valeur_ouverture = 0

        for ticker, (prix, ouverture) in prix_actuels.items():
            quantite = titres[ticker]["quantite"]

            valeur_totale += prix * quantite
            valeur_ouverture += ouverture * quantite

        variation_portfolio = valeur_totale - valeur_ouverture

        self.label_valeur.config(
            text=f"Valeur totale : {valeur_totale:.2f} $"
        )

        symbole = "▲" if variation_portfolio >= 0 else "▼"

        self.label_variation.config(
            text=f"{symbole} {abs(variation_portfolio):.2f} $ depuis l'ouverture",
            fg="green" if variation_portfolio >= 0 else "red"
        )