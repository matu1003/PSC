from otree.api import *
c = cu

doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'SL5'
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
        for j in [j1, j2]:
            j.participant.vars["total_score"] = 0
            j.participant.vars["pseudo"] = ""

class Group(BaseGroup):
    final_choice = models.StringField()

def calcul_meilleur_choix(group: Group):
    player1, player2 = group.get_players()

    # Le choix final est celui sélectionné par J2 (stocké dans rank1)
    group.final_choice = player2.rank1

            # Attribution des scores en fonction du classement dans `preference_profile`
    for player in [player1, player2]:
                if group.final_choice in player.preference_profile.split(","):
                    player.round_score = (6 - (player.preference_profile.split(",").index(group.final_choice) + 1))**2
                else:
                    player.round_score = 0  # Sécurité si jamais le choix final n'est pas trouvé

                # Ajout au score total
                player.participant.vars["total_score"] += player.round_score
class Player(BasePlayer):
    pseudo = models.StringField()
    preference_profile = models.StringField()
    opponent_profile = models.StringField()
    selected_choice = models.StringField()
    round_score = models.IntegerField(initial=0, max=5, min=1)
    choix = models.StringField()
    choix1 = models.StringField()
    choix2 = models.StringField()
    choix3 = models.StringField()
    rank1 = models.StringField()

class Page_Accueil(Page):
    form_model = 'player'
    form_fields = ['pseudo']
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {'total_score': player.participant.vars["total_score"]}

    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['pseudo'] = player.pseudo

    def error_message(player: Player, values):
        if values['pseudo'] == "":
            return "Vous n'avez pas choisi de pseudo"


class Presentation_SL(Page):
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
                    (rank + 1, my_choice, (6-rank-1)**2, opp_choice)
                    for rank, (my_choice, opp_choice) in enumerate(zip(my_profile, opponent_profile))
                ]
        return {
                    'my_profile': player.preference_profile.split(","),
                    'opponent_profile': player.opponent_profile.split(","),
                    'combined_profiles': combined_profiles,  # Liste [(1, 'A', 'E'), (2, 'B', 'D'), ...]
                    'total_score': player.participant.vars["total_score"]
                }
class Choix(Page):
    form_model = 'player'
    form_fields = ['choix1', 'choix2', 'choix3']
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return player.id_in_group == 1

    @staticmethod
    def vars_for_template(player: Player):
        my_profile = player.preference_profile.split(",")
        opponent_profile = player.opponent_profile.split(",")
        combined_profiles = [
                    (rank + 1, my_choice, (6-rank-1)**2,opp_choice)
                    for rank, (my_choice, opp_choice) in enumerate(zip(my_profile, opponent_profile))
                ]

        return {
                    'my_profile': player.preference_profile.split(","),
                    'opponent_profile': player.opponent_profile.split(","),
                    'combined_profiles': combined_profiles,  # Liste prête pour le tableau
                    'total_score': player.participant.vars["total_score"]
                }
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # Récupérer les vétos depuis le formulaire HTML
                player.choix = f"{player.choix1},{player.choix2},{player.choix3}"


    @staticmethod
    def error_message(player: Player, values):

        """ Vérifie qu'un même choix ne soit pas sélectionné plusieurs fois """
        selected_choices = [
            values["choix1"], values["choix2"], values["choix3"]
        ]

        if len(set(selected_choices)) != len(selected_choices):
            return "Vous ne pouvez pas sélectionner plusieurs fois le même choix (veto et classement)."
class J2_attente_veto_de_J1(WaitPage):
    title_text = 'Attente des 3 choix du premier joueur'
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return player.id_in_group == 2
class Choix_de_J2(Page):
    form_model = 'player'
    form_fields = ['rank1']
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return player.id_in_group == 2
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        player1 = group.get_player_by_id(1)
        player2 = group.get_player_by_id(2)
        my_profile = player.preference_profile.split(",")
        opponent_profile = player.opponent_profile.split(",")
        all_choices = player2.preference_profile.split(",")
        remaining_choices = player1.choix.split(",")


        combined_profiles = [
                    (rank + 1, my_choice, (6-rank-1)**2, opp_choice)
                    for rank, (my_choice, opp_choice) in enumerate(zip(my_profile, opponent_profile))
                ]

        return {    "remaining_choices": remaining_choices,
                    'my_profile': player.preference_profile.split(","),
                    'opponent_profile': player.opponent_profile.split(","),
                    'combined_profiles': combined_profiles, # Liste prête pour le tableau
                     "choix1": player1.choix1,
                     "choix2": player1.choix2,
                     "choix3": player1.choix3,
                     'total_score': player.participant.vars["total_score"]
                }
class J1_attente_de_J2(WaitPage):
    after_all_players_arrive = calcul_meilleur_choix
    @staticmethod
    def is_displayed(player: Player):
        group = player.group
        return player.id_in_group==1
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
                'total_score': player.participant.vars["total_score"]
            }

class Attente_Avant_Resultat(WaitPage):
    title_text = "Un instant..."
    body_text = "En attente des autres joueurs pour le classement final"
    wait_for_all_groups = True
    def is_displayed(player: Player):
        return player.round_number == 4

class pageFinale(Page):
    form_model = 'player'
    def is_displayed(player: Player):
        return player.round_number == 4

    def vars_for_template(player: Player):
        players = player.subsession.get_players()
        score = player.participant.vars["total_score"]
        scores = [(p.participant.vars["pseudo"],p.participant.vars["total_score"]) for p in players]
        scores.sort(key=lambda x: x[1], reverse=True)
        classement = 1+scores.index((player.participant.vars["pseudo"], score))
        meilleur_score = scores[0][1]
        leaderboard = [(i+1, ps, sc) for i, (ps, sc) in enumerate(scores)]
        return {"score": score,
                "classement": classement,
                "scorePrem": meilleur_score,
                "detail": leaderboard}

page_sequence = [Page_Accueil, Presentation_SL, Attribution_des_profils, Choix, J2_attente_veto_de_J1, Choix_de_J2, J1_attente_de_J2, CalculScoreChoix, Attente_Avant_Resultat, pageFinale]
