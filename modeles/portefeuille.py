from modeles.sujet import Sujet
import yfinance as yf


TITRES = {
    "AAPL": {
        "quantite": 10,
        "seuil_haut": 200.0,
        "seuil_bas": 150.0
    },
    "GOOGL": {
        "quantite": 5,
        "seuil_haut": 160.0,
        "seuil_bas": 120.0
    },
    "MSFT": {
        "quantite": 8,
        "seuil_haut": 430.0,
        "seuil_bas": 380.0
    }
}


def recuperer_prix(ticker):
    """Retourne le prix actuel et le prix d'ouverture."""
    info = yf.Ticker(ticker).fast_info
    prix = info["last_price"]

    if prix is None:
        raise ValueError(f"Le titre '{ticker}' n'existe pas.")

    return prix, info["open"]


class Portefeuille(Sujet):

    def __init__(self):
        super().__init__()

        self._titres = {ticker: donnees.copy()
            for ticker, donnees in TITRES.items()}

        self._prix_actuels = {}

    def ajouter_titre(self, ticker, quantite, prix, 
                      seuil_haut=None, seuil_bas=None):
        self._titres[ticker] = {"quantite": quantite, "seuil_haut": round(seuil_haut if seuil_haut is not None else prix * 1.2, 2),
            "seuil_bas": round(seuil_bas if seuil_bas is not None else prix * 0.8, 2)}

        self.notifier()

    def retirer_titre(self, ticker):
        del self._titres[ticker]
        self._prix_actuels.pop(ticker, None)
        self.notifier()

    def modifier_quantite_action(self, ticker, quantite):
        self._titres[ticker]["quantite"] = quantite
        self.notifier()

    def modifier_seuils(self, ticker, seuil_haut=None, seuil_bas=None):
        if seuil_bas is not None:
            self._titres[ticker]["seuil_bas"] = round(seuil_bas, 2)

        if seuil_haut is not None:
            self._titres[ticker]["seuil_haut"] = round(seuil_haut, 2)

        self.notifier()

    def mettre_a_jour_prix(self):
        self._prix_actuels = {ticker: recuperer_prix(ticker)
            for ticker in self._titres}

        self.notifier()

    def get_donnees(self) -> dict:
        return {
            "titres": self._titres,
            "prix_actuels": self._prix_actuels 
            } 