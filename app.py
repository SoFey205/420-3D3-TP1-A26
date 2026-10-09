
import tkinter as tk
from datetime import datetime

from modeles.portefeuille import Portefeuille, recuperer_prix
from observateurs.prix import Prix
from observateurs.valeur_total import ValeurTotale
from observateurs.logger import Logger
from observateurs.alerte import Alerte


INTERVALLE_MS = 30000

POLICE = ("Segoe UI", 10)
POLICE_TITRE = ("Segoe UI", 16, "bold")
POLICE_VALEUR = ("Segoe UI", 13, "bold")


def entier_positif(texte):
    """Convertit texte en entier strictement positif."""
    valeur = int(texte)
    if valeur <= 0:
        raise ValueError
    return valeur


def flottant_positif(texte):
    """Convertit texte en nombre décimal strictement positif."""
    valeur = float(texte)
    if valeur <= 0:
        raise ValueError
    return valeur


class App:
    def __init__(self):
        self.portefeuille = Portefeuille()

        self.fenetre = tk.Tk()
        self.fenetre.title("Portfolio Tracker")
        self.fenetre.resizable(False, False)
        self.fenetre.option_add("*Font", POLICE)

        self.labels_prix = {}
        self.frames_prix = {}

        tk.Label(
            self.fenetre,
            text="Portfolio Tracker",
            font=POLICE_TITRE
        ).pack(pady=10)

        # Section des prix
        self.frame_prix = tk.LabelFrame(
            self.fenetre,
            text="Prix en temps réel",
            padx=10,
            pady=10
        )
        self.frame_prix.pack(fill=tk.X, padx=10, pady=5)

        for ticker in self.portefeuille.get_donnees()["titres"]:
            self._creer_ligne_prix(ticker)

        # Section de gestion des titres
        self._construire_gestion()

        # Section du résumé du portefeuille
        frame_portfolio = tk.LabelFrame(
            self.fenetre,
            text="Mon portfolio",
            padx=10,
            pady=10
        )
        frame_portfolio.pack(fill=tk.X, padx=10, pady=5)

        self.label_valeur = tk.Label(
            frame_portfolio,
            text="Valeur totale : calcul en cours...",
            font=POLICE_VALEUR
        )
        self.label_valeur.pack()

        self.label_variation = tk.Label(frame_portfolio, text="")
        self.label_variation.pack()

        # Section des alertes
        frame_alertes = tk.LabelFrame(
            self.fenetre,
            text="Alertes",
            padx=10,
            pady=10
        )
        frame_alertes.pack(fill=tk.X, padx=10, pady=5)

        self.label_alertes = tk.Label(
            frame_alertes,
            text="Aucune alerte",
            fg="gray",
            justify=tk.LEFT,
            wraplength=380
        )
        self.label_alertes.pack(anchor="w")

        self.label_maj = tk.Label(
            self.fenetre,
            text="",
            font=("Segoe UI", 9),
            fg="gray"
        )
        self.label_maj.pack(pady=5)

        # Création et abonnement des observateurs
        self.observateur_prix = Prix(self.labels_prix)
        self.observateur_valeur_totale = ValeurTotale(
            self.label_valeur,
            self.label_variation
        )
        self.observateur_logger = Logger()
        self.observateur_alerte = Alerte(self.label_alertes)

        self.portefeuille.abonner(self.observateur_prix)
        self.portefeuille.abonner(self.observateur_valeur_totale)
        self.portefeuille.abonner(self.observateur_logger)
        self.portefeuille.abonner(self.observateur_alerte)

        # Premier chargement et boucle automatique
        self.rafraichir()
        self.fenetre.mainloop()

    # ------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------

    def _construire_gestion(self):
        frame = tk.LabelFrame(
            self.fenetre,
            text="Gérer les titres",
            padx=10,
            pady=10
        )
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Formulaire d'ajout
        ligne_ajout = tk.Frame(frame)
        ligne_ajout.pack(fill=tk.X)

        self.entry_ticker = self._champ(
            ligne_ajout, "Ticker", width=8
        )
        self.entry_quantite = self._champ(
            ligne_ajout, "Qté", width=5, valeur_defaut="1"
        )
        self.entry_seuil_bas_ajout = self._champ(
            ligne_ajout, "Alerte basse", width=7
        )
        self.entry_seuil_haut_ajout = self._champ(
            ligne_ajout, "Alerte haute", width=7
        )

        tk.Button(
            ligne_ajout,
            text="Ajouter",
            command=self.ajouter_titre
        ).pack(side=tk.LEFT)

        tk.Label(
            frame,
            text=(
                "(Alertes optionnelles : si vides, calculées "
                "à ±20% du prix actuel)"
            ),
            font=("Segoe UI", 8),
            fg="gray"
        ).pack(anchor="w", pady=(2, 5))

        # Liste des titres
        ligne_liste = tk.Frame(frame)
        ligne_liste.pack(fill=tk.X)

        self.listbox_titres = tk.Listbox(
            ligne_liste,
            height=4,
            exportselection=False
        )
        self.listbox_titres.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True
        )

        for ticker in self.portefeuille.get_donnees()["titres"]:
            self.listbox_titres.insert(
                tk.END,
                self._texte_listbox(ticker)
            )

        tk.Button(
            ligne_liste,
            text="Retirer",
            command=self.retirer_titre
        ).pack(side=tk.LEFT, padx=(5, 0), anchor="n")

        # Formulaire de modification
        ligne_modif = tk.Frame(frame)
        ligne_modif.pack(fill=tk.X, pady=(8, 0))

        tk.Label(ligne_modif, text="Sélection →").pack(side=tk.LEFT)

        self.entry_nouvelle_quantite = self._champ(
            ligne_modif, "Qté", width=5
        )
        self.entry_nouveau_seuil_bas = self._champ(
            ligne_modif, "Alerte basse", width=7
        )
        self.entry_nouveau_seuil_haut = self._champ(
            ligne_modif, "Alerte haute", width=7
        )

        tk.Button(
            ligne_modif,
            text="Modifier sélection",
            command=self.modifier_selection
        ).pack(side=tk.LEFT)

        self.label_statut_titres = tk.Label(
            frame,
            text="",
            font=("Segoe UI", 9),
            fg="gray"
        )
        self.label_statut_titres.pack(anchor="w", pady=(5, 0))

    def _champ(self, parent, texte, width, valeur_defaut=""):
        tk.Label(parent, text=f"{texte}:").pack(side=tk.LEFT)

        entry = tk.Entry(parent, width=width)

        if valeur_defaut:
            entry.insert(0, valeur_defaut)

        entry.pack(side=tk.LEFT, padx=(2, 8))
        return entry

    def _creer_ligne_prix(self, ticker):
        frame = tk.Frame(self.frame_prix)
        frame.pack(fill=tk.X, pady=2)

        tk.Label(
            frame,
            text=f"{ticker}:",
            width=8,
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        ).pack(side=tk.LEFT)

        label = tk.Label(frame, text="Chargement...")
        label.pack(side=tk.LEFT)

        self.labels_prix[ticker] = label
        self.frames_prix[ticker] = frame

    def _texte_listbox(self, ticker):
        titres = self.portefeuille.get_donnees()["titres"]
        infos = titres[ticker]

        return (
            f"{ticker} — {infos['quantite']} action(s) "
            f"(alerte : {infos['seuil_bas']:.2f} $ / "
            f"{infos['seuil_haut']:.2f} $)"
        )

    def _rafraichir_ligne_listbox(self, index, ticker):
        self.listbox_titres.delete(index)
        self.listbox_titres.insert(
            index,
            self._texte_listbox(ticker)
        )
        self.listbox_titres.selection_set(index)

    def _ticker_selectionne(self):
        selection = self.listbox_titres.curselection()

        if not selection:
            return None

        index = selection[0]
        texte = self.listbox_titres.get(index)
        ticker = texte.split(" — ")[0]

        return index, ticker

    def _statut(self, texte, couleur):
        self.label_statut_titres.config(
            text=texte,
            fg=couleur
        )

    # ------------------------------------------------------------
    # Actions sur les titres
    # ------------------------------------------------------------

    def ajouter_titre(self):
        ticker = self.entry_ticker.get().strip().upper()

        if not ticker:
            return

        titres = self.portefeuille.get_donnees()["titres"]

        if ticker in titres:
            self._statut(
                f"{ticker} est déjà dans le portfolio.",
                "orange"
            )
            return

        try:
            quantite = entier_positif(
                self.entry_quantite.get().strip()
            )
        except ValueError:
            self._statut(
                "La quantité doit être un nombre entier positif.",
                "red"
            )
            return

        texte_bas = self.entry_seuil_bas_ajout.get().strip()
        texte_haut = self.entry_seuil_haut_ajout.get().strip()

        try:
            seuil_bas = (
                flottant_positif(texte_bas) if texte_bas else None
            )
            seuil_haut = (
                flottant_positif(texte_haut) if texte_haut else None
            )
        except ValueError:
            self._statut(
                "Les alertes doivent être des nombres positifs.",
                "red"
            )
            return

        if (
            seuil_bas is not None
            and seuil_haut is not None
            and seuil_bas >= seuil_haut
        ):
            self._statut(
                "L'alerte basse doit être inférieure à l'alerte haute.",
                "red"
            )
            return

        # Vérifier que le ticker existe et récupérer son prix initial
        try:
            prix, _ = recuperer_prix(ticker)
        except Exception:
            self._statut(
                f"Impossible de récupérer les données de '{ticker}'.",
                "red"
            )
            return

        # Le modèle conserve les données du titre
        self.portefeuille.ajouter_titre(
            ticker,
            quantite,
            prix,
            seuil_haut,
            seuil_bas
        )

        # Mettre à jour l'interface
        self._creer_ligne_prix(ticker)
        self.listbox_titres.insert(
            tk.END,
            self._texte_listbox(ticker)
        )

        for entry, valeur in (
            (self.entry_ticker, ""),
            (self.entry_quantite, "1"),
            (self.entry_seuil_bas_ajout, ""),
            (self.entry_seuil_haut_ajout, "")
        ):
            entry.delete(0, tk.END)
            if valeur:
                entry.insert(0, valeur)

        self._statut(
            f"{ticker} ajouté au portfolio ({quantite} action(s)).",
            "green"
        )

        # Récupérer les prix et avertir les observateurs
        self.rafraichir()

    def retirer_titre(self):
        selectionne = self._ticker_selectionne()

        if selectionne is None:
            self._statut(
                "Sélectionnez un titre à retirer.",
                "orange"
            )
            return

        index, ticker = selectionne

        self.listbox_titres.delete(index)

        # Le modèle retire le titre et son prix mémorisé
        self.portefeuille.retirer_titre(ticker)

        self.labels_prix.pop(ticker, None)
        self.frames_prix.pop(ticker).destroy()

        self._statut(
            f"{ticker} retiré du portfolio.",
            "gray"
        )

    def modifier_selection(self):
        selectionne = self._ticker_selectionne()

        if selectionne is None:
            self._statut(
                "Sélectionnez un titre à modifier.",
                "orange"
            )
            return

        index, ticker = selectionne

        texte_qte = self.entry_nouvelle_quantite.get().strip()
        texte_bas = self.entry_nouveau_seuil_bas.get().strip()
        texte_haut = self.entry_nouveau_seuil_haut.get().strip()

        if not texte_qte and not texte_bas and not texte_haut:
            self._statut(
                "Entrez une nouvelle quantité et/ou de nouvelles alertes.",
                "orange"
            )
            return

        changements = []

        try:
            if texte_qte:
                quantite = entier_positif(texte_qte)

                self.portefeuille.modifier_quantite_action(
                    ticker, quantite
                )
                changements.append(f"{quantite} action(s)")

            if texte_bas or texte_haut:
                if not (texte_bas and texte_haut):
                    self._statut(
                        "Les deux alertes doivent être fournies ensemble.",
                        "red"
                    )
                    return

                seuil_bas = flottant_positif(texte_bas)
                seuil_haut = flottant_positif(texte_haut)

                if seuil_bas >= seuil_haut:
                    self._statut(
                        "L'alerte basse doit être inférieure à l'alerte haute.",
                        "red"
                    )
                    return

                self.portefeuille.modifier_seuils(
                    ticker,
                    seuil_haut=seuil_haut,
                    seuil_bas=seuil_bas
                )

                changements.append(
                    f"alertes {seuil_bas:.2f} $ / {seuil_haut:.2f} $"
                )

        except ValueError:
            self._statut(
                "La quantité et les alertes doivent être des nombres positifs.",
                "red"
            )
            return

        self._rafraichir_ligne_listbox(index, ticker)

        for entry in (
            self.entry_nouvelle_quantite,
            self.entry_nouveau_seuil_bas,
            self.entry_nouveau_seuil_haut
        ):
            entry.delete(0, tk.END)

        self._statut(
            f"{ticker} mis à jour : {', '.join(changements)}.",
            "green"
        )

    # ------------------------------------------------------------
    # Actualisation des données
    # ------------------------------------------------------------

    def rafraichir(self):
        """Récupère les prix, puis laisse les observateurs actualiser
        les prix, le résumé, les alertes et le journal CSV."""

        try:
            self.portefeuille.mettre_a_jour_prix()

            horodatage = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            self.label_maj.config(
                text=f"Dernière mise à jour : {horodatage}",
                fg="gray"
            )

        except Exception as erreur:
            self.label_maj.config(
                text=f"Erreur : {erreur}",
                fg="red"
            )

        # Le prochain cycle est planifié même si une erreur survient
        self.fenetre.after(
            INTERVALLE_MS,
            self.rafraichir
        )


if __name__ == "__main__":
    App()