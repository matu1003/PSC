
from otree.api import *
c = cu

doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'liste_aveugle_basique_3'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    CHOIXA = 'A'
    CHOIXB = 'B'
    CHOIXC = 'C'
class Subsession(BaseSubsession):
    pass
class Group(BaseGroup):
    Meilleurchoix = models.StringField()
def best_choice(group: Group):
    import random
    players = group.get_players()
    
    # Extraction des classements des deux joueurs
    player1_choices = {
            'CHOIX_1': players[0].CHOIX_1,
            'CHOIX_2': players[0].CHOIX_2,
            'CHOIX_3': players[0].CHOIX_3
        }
    
    player2_choices = {
            'CHOIX_1': players[1].CHOIX_1,
            'CHOIX_2': players[1].CHOIX_2,
            'CHOIX_3': players[1].CHOIX_3
        }
    
    scores = {'A': 0, 'B': 0, 'C': 0}
    
    for player_choices in [player1_choices, player2_choices]:
          for rank, choice in player_choices.items():
                if rank == 'CHOIX_1':
                    scores[choice] += 3
                elif rank == 'CHOIX_2':
                    scores[choice] += 2
                elif rank == 'CHOIX_3':
                    scores[choice] += 1
    
    
    max_score = max(scores.values())
    top_choices = [choice for choice, score in scores.items() if score == max_score]
    
    group.Meilleurchoix=random.choice(top_choices)
    
    
class Player(BasePlayer):
    CHOIX_1 = models.StringField(choices=[['A', 'A'], ['B', 'B'], ['C', 'C']])
    CHOIX_2 = models.StringField(choices=[['A', 'A'], ['B', 'B'], ['C', 'C']])
    CHOIX_3 = models.StringField(choices=[['A', 'A'], ['B', 'B'], ['C', 'C']])
def custom_export(players):
    yield ['participant_code', 'id_in_group']
    for p in players:
        pp = p.participant
        yield [pp.code, p.id_in_group]
class PRESENTATION(Page):
    form_model = 'player'
class Choix(Page):
    form_model = 'player'
    form_fields = ['CHOIX_1', 'CHOIX_2', 'CHOIX_3']
    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        pass
class Waiting(WaitPage):
    after_all_players_arrive = best_choice
class Results(Page):
    form_model = 'player'
page_sequence = [PRESENTATION, Choix, Waiting, Results]