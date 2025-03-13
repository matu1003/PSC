
from otree.api import *
c = cu

doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'VR5'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 4
class Subsession(BaseSubsession):
    pass
def creating_session(subsession: Subsession):
    session = subsession.session
    PROFILES_J2 = {
                1: ["Buffle", "Fourmi", "Aigle", "Lama", "Hippocampe"],
                2: ["Fourmi", "Lama", "Hippocampe", "Buffle", "Aigle"],
                3: ["Aigle", "Lama", "Hippocampe", "Fourmi", "Buffle"],
                4: ["Buffle", "Aigle", "Hippocampe", "Lama", "Fourmi"],
            }
    
    for group in subsession.get_groups():
        players = group.get_players()
        j1 = players[0]  # Joueur 1
        j2 = players[1]  # Joueur 2
    
                # J1 a toujours le même profil
        j1.preference_profile = "Hippocampe,Lama,Aigle,Fourmi,Buffle"
    
                # J2 reçoit un profil en fonction du round
        j2.preference_profile = ",".join(PROFILES_J2[subsession.round_number])
    
                # Définition du profil de l'adversaire
        j1.opponent_profile = j2.preference_profile
        j2.opponent_profile = j1.preference_profile
class Group(BaseGroup):
    final_choice = models.StringField()
def calcul_meilleur_choix(group: Group):
    import random
    player1, player2 = group.get_players()
    
        # Récupérer les vétos
    veto_p1 = set(player1.vetos.split(",")) if player1.vetos else set()
    veto_p2 = set(player2.vetos.split(",")) if player2.vetos else set()
    
        # Exclure les choix véto
    remaining_choices = set(player1.preference_profile.split(",")) - (veto_p1 | veto_p2)
    
        # Récupérer les classements imposés (préférences initiales)
    
    
        # Récupérer le classement des choix restants
    ranking_p1 = player1.ranking.split(",")
    ranking_p2 = player2.ranking.split(",")
    
        # Attribuer un score à chaque choix restant basé sur `preference_profile`
    score_choices = {}
    for choice in remaining_choices:
            score_p1 = 6 - (ranking_p1.index(choice) + 1) if choice in ranking_p1 else 0
            score_p2 = 6 - (ranking_p2.index(choice) + 1) if choice in ranking_p2 else 0
            score_choices[choice] = score_p1 + score_p2  # Somme des scores des deux joueurs
    
        # Déterminer le(s) choix avec le score maximum
    max_score = max(score_choices.values(), default=0)
    best_choices = [c for c, score in score_choices.items() if score == max_score]
    
        # Tirage au sort en cas d'égalité
    final_choice = random.choice(best_choices) if best_choices else "Aucun choix possible"
    
        # Enregistrer le choix final et calculer le score en fonction des préférences initiales
    for leplayer in [player1, player2]:
            leplayer.selected_choice = final_choice
            leplayer.round_score = 6 - (leplayer.preference_profile.split(",").index(final_choice) + 1) if final_choice in leplayer.preference_profile.split(",") else 0
    
    player1.total_score += player1.round_score
    player2.total_score += player2.round_score  # Score cumulé
    group.final_choice=final_choice
    
class Player(BasePlayer):
    preference_profile = models.StringField()
    opponent_profile = models.StringField()
    vetos = models.StringField()
    ranking = models.StringField()
    selected_choice = models.StringField()
    round_score = models.IntegerField(initial=0, max=5, min=1)
    total_score = models.IntegerField(initial=0)
    veto1 = models.StringField()
    veto2 = models.StringField()
    rank1 = models.StringField()
    rank2 = models.StringField()
    rank3 = models.StringField()
class Page_Accueil(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
class Presentation_VR(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1
class Attribution_des_profils(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        my_profile = player.preference_profile.split(",")
        opponent_profile = player.opponent_profile.split(",")
        combined_profiles = [
                    (rank + 1, my_choice, opp_choice)
                    for rank, (my_choice, opp_choice) in enumerate(zip(my_profile, opponent_profile))
                ]
        return {
                    'my_profile': player.preference_profile.split(","),
                    'opponent_profile': player.opponent_profile.split(","),
                    'combined_profiles': combined_profiles  # Liste [(1, 'A', 'E'), (2, 'B', 'D'), ...]
        
                }
class Veto_Et_Classement(Page):
    form_model = 'player'
    form_fields = ['veto1', 'veto2', 'rank1', 'rank2', 'rank3']
    @staticmethod
    def vars_for_template(player: Player):
        my_profile = player.preference_profile.split(",")
        opponent_profile = player.opponent_profile.split(",")
        combined_profiles = [
                    (rank + 1, my_choice, opp_choice)
                    for rank, (my_choice, opp_choice) in enumerate(zip(my_profile, opponent_profile))
                ]
        
        return {
                    'my_profile': player.preference_profile.split(","),
                    'opponent_profile': player.opponent_profile.split(","),
                    'combined_profiles': combined_profiles  # Liste prête pour le tableau
                }
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Récupérer les vétos depuis le formulaire HTML
                player.vetos = f"{player.veto1},{player.veto2}"
        
                # Récupérer et stocker le classement sous forme "c,d,e"
                player.ranking = f"{player.rank1},{player.rank2},{player.rank3}"
    @staticmethod
    def error_message(player: Player, values):
        
        """ Vérifie qu'un même choix ne soit pas sélectionné plusieurs fois """
        selected_choices = [
            values["veto1"], values["veto2"], 
            values["rank1"], values["rank2"], values["rank3"]
        ]
        
        if len(set(selected_choices)) != len(selected_choices):
            return "Vous ne pouvez pas sélectionner plusieurs fois le même choix (veto et classement)."
class Attente_Avant_Tirage_Score(WaitPage):
    after_all_players_arrive = calcul_meilleur_choix
class CalculScoreChoix(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        player1,player2 =group.get_players()
        return {
                "final_choice": group.final_choice,
                "score_p1": player1.round_score,
                "score_p2": player2.round_score,
            }
page_sequence = [Page_Accueil, Presentation_VR, Attribution_des_profils, Veto_Et_Classement, Attente_Avant_Tirage_Score, CalculScoreChoix]