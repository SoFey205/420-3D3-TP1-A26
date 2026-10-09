from observateurs.observateur import Observateur


class Alerte(Observateur):

    def __init__(self, label_alertes):
        self.label_alertes = label_alertes

    def actualiser(self, sujet):
        donnees = sujet.get_donnees()
        titres = donnees["titres"]
        prix_actuels = donnees["prix_actuels"]

        alertes = []
        for ticker, (prix, _) in prix_actuels.items():
            seuil_haut = titres[ticker]["seuil_haut"]
            seuil_bas = titres[ticker]["seuil_bas"]

            if prix >= seuil_haut:
                alertes.append(
                    f"⚠️ {ticker} dépasse le seuil haut "
                    f"({prix:.2f} $ ≥ {seuil_haut:.2f} $)"
                )
            elif prix <= seuil_bas:
                alertes.append(
                    f"⚠️ {ticker} sous le seuil bas "
                    f"({prix:.2f} $ ≤ {seuil_bas:.2f} $)"
                )

        self.label_alertes.config(
            text="\n".join(alertes) if alertes else "Aucune alerte",
            fg="red" if alertes else "gray",
        )