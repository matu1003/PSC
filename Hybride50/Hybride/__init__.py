from otree.api import *
import random
c = cu

doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'Hybride'
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

        #Initialisation du score total via participant:
        for leplayer in [j1, j2]:
            leplayer.participant.vars["total_score"] = 0
            leplayer.participant.vars["pseudo"] = ""


class Group(BaseGroup):
    methode_utilisee = models.IntegerField()
    choix_final = models.StringField()


def set_best_choice(group: Group):
    p1 = group.get_player_by_id(1)
    p2 = group.get_player_by_id(2)

    profile1 = [p1.choix_1, p1.choix_2, p1.choix_3, p1.choix_4, p1.choix_5]
    profile2 = [p2.choix_1, p2.choix_2, p2.choix_3, p2.choix_4, p2.choix_5]

    methode = random.choice([1, 2])
    group.methode_utilisee = methode  # stocke la méthode utilisée

    if methode == 1:
            # MÉTHODE 1 : somme des classements (hors choix 4 et 5 des deux joueurs)
            banned_choices = set(profile1[3:] + profile2[3:])
            pool = [c for c in set(profile1 + profile2) if c not in banned_choices]

            score_map = {}
            for c in pool:
                score_p1 = profile1.index(c) + 1 if c in profile1 else 6
                score_p2 = profile2.index(c) + 1 if c in profile2 else 6
                total_score = score_p1 + score_p2
                if total_score not in score_map:
                    score_map[total_score] = []
                score_map[total_score].append(c)

            best_score = min(score_map.keys())
            candidates = score_map[best_score]
            final_choice = random.choice(candidates)
    else:
            # MÉTHODE 2 : garder les 3 premiers choix de joueur 1 et choisir le plus haut selon joueur 2
            pool = [c for c in profile1[:3]]

            ranked_pool = [c for c in profile2 if c in pool]
            final_choice = ranked_pool[0] if ranked_pool else random.choice(pool)

    #Calcul des scores finaux:
    for p in [p1,p2]:
        score = 5 - p.preference_profile.split(",").index(final_choice)
        p.participant.vars["total_score"] += score

    group.choix_final = final_choice

class Player(BasePlayer):
    pseudo = models.StringField()
    choix_1 = models.StringField()
    choix_2 = models.StringField()
    choix_3 = models.StringField()
    choix_4 = models.StringField()
    choix_5 = models.StringField()
    preference_profile = models.StringField()
    opponent_profile = models.StringField()
    round_score = models.IntegerField()


class Page_Accueil(Page):
    form_model = 'player'
    form_model = 'player'
    form_fields = ['pseudo']
    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    def before_next_page(player: Player, timeout_happened):
        player.participant.vars['pseudo'] = player.pseudo

    def error_message(player: Player, values):
        if values['pseudo'] == "":
            return "Vous n'avez pas choisi de pseudo"


class Mecanisme_VR(Page):
    form_model = 'player'
    def is_displayed(self):
        return self.round_number == 1

class Mecanisme_SL(Page):
    form_model = 'player'
    def is_displayed(self):
        return self.round_number == 1


class Mecanisme_hybride(Page):
    form_model = 'player'
    def is_displayed(self):
        return self.round_number == 1


class Exemple_hybride(Page):
    form_model = 'player'
    def is_displayed(self):
        return self.round_number == 1


class Attribution_profil_preference(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player: Player):
        my_profile = player.preference_profile.split(",") ##BUG
        opponent_profile = player.opponent_profile.split(",")
        combined_profiles = [
                    (rank + 1, my_choice, opp_choice, 5 - rank)
                    for rank, (my_choice, opp_choice) in enumerate(zip(my_profile, opponent_profile))
                ]
        return {
                    'my_profile': player.preference_profile.split(","),
                    'opponent_profile': player.opponent_profile.split(","),
                    'combined_profiles': combined_profiles,  # Liste [(1, 'A', 'E'), (2, 'B', 'D'), ...]
                    'total_score': player.participant.vars["total_score"]
                }
class Classement_voeux(Page):
    form_model = 'player'
    form_fields = ['choix_1', 'choix_2', 'choix_3', 'choix_4', 'choix_5']
    @staticmethod
    def vars_for_template(player: Player):
        my_profile = player.preference_profile.split(",")
        opponent_profile = player.opponent_profile.split(",")
        combined_profiles = [
                    (rank + 1, my_choice, opp_choice, 5 - rank)
                    for rank, (my_choice, opp_choice) in enumerate(zip(my_profile, opponent_profile))
                ]

        return {
                    'my_profile': player.preference_profile.split(","),
                    'opponent_profile': player.opponent_profile.split(","),
                    'combined_profiles': combined_profiles,  # Liste prête pour le tableau
                    'total_score': player.participant.vars["total_score"]
                }
    @staticmethod
    def error_message(player: Player, values):
        """ Vérifie qu'un même choix ne soit pas sélectionné plusieurs fois """
        selected_choices = [
                    values["choix_1"], values["choix_2"],
                    values["choix_3"], values["choix_4"], values["choix_5"]
                ]

        if len(set(selected_choices)) != len(selected_choices):
            return "Vous ne pouvez pas sélectionner plusieurs fois le même choix."

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


class Calcul_resultat(WaitPage):
    after_all_players_arrive = set_best_choice

class Attente_Avant_Resultat(WaitPage):
    title_text = "Un instant..."
    body_text = "En attente des autres joueurs pour le classement final"
    wait_for_all_groups = True
    def is_displayed(player: Player):
        return player.round_number == 4

class Results(Page):
    form_model = 'player'

    def vars_for_template(player: Player):
        return {'total_score': player.participant.vars["total_score"]}

page_sequence = [Page_Accueil, Mecanisme_VR, Mecanisme_SL, Mecanisme_hybride, Exemple_hybride, Attribution_profil_preference, Classement_voeux, Calcul_resultat, Results, Attente_Avant_Resultat, pageFinale]
