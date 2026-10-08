from app import TITRES, entier_positif
from modeles.sujet import Sujet, portefeuille
import yfinance as yf

def recuperer_prix(ticker):
    """Retourne (prix, ouverture) pour un ticker, ou lève une erreur s'il est introuvable."""
    info = yf.Ticker(ticker).fast_info
    prix = info["last_price"]
    if prix is None:
        raise ValueError(f"Le titre '{ticker}' n'existe pas.")
    return prix, info["open"]

class Portefeuille(Sujet):

    def __init__(self):
        super().__init__()
        self._titres = {}
        self._prix_actuels = {}
    def ajouter_titre(self, ticker, quantite, prix, seuil_haut=None, seuil_bas=None):
        """
        Ajoute un titre au portefeuille.
        """
        self._titres[ticker] = {
             "quantite": quantite,
             "seuil_haut": round(seuil_haut if seuil_haut is not None else prix * 1.2, 2),
             "seuil_bas": round(seuil_bas if seuil_bas is not None else prix * 0.8, 2),
                }
        self.notifier()
        
        
        pass
    def retirer_titre(self, ticker):
        """
        Retire un titre du portefeuille.
        """
        del self._titres[ticker]
        self.notifier()

    def modifier_quantite_action(self, ticker, quantite):
        """
        Met à jour la quantité d'actions d'un titre dans le portefeuille.
        """
        self._titres[ticker]["quantite"] = quantite
        self.notifier()

    def modifier_seuils(self, ticker, seuil_haut=None, seuil_bas=None): #À AJOUTER DANS UMLLLL
        """
        Met à jour les seuils d'un titre dans le portefeuille.
        """
        self._titres[ticker]["seuil_bas"] = round(seuil_bas, 2)
        self._titres[ticker]["seuil_haut"] = round(seuil_haut, 2)
        self.notifier()

    def mettre_a_jour_prix(self, prix_actuels):
        """ 
        Met à jour le prix d'un titre dans le portefeuille.
        """
        self._prix_actuels = {ticker: recuperer_prix(ticker) for ticker in self._titres.keys()}
        self.notifier()

    def get_donnees(self):
        """
        Récupère les données du portefeuille.
        """
        return {
            "titres": self._titres,
            "prix_actuels": self._prix_actuels
        } 
    