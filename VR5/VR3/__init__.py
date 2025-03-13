
from otree.api import *
c = cu

doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'VR3'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10
class Subsession(BaseSubsession):
    pass
class Group(BaseGroup):
    remaining_choices = models.StringField()
    best_choice = models.StringField()
def calculate_remaining_choice(group: Group):
    all_choices = {'A', 'B', 'C'}
    vetoes = {p.Veto_1 for p in group.get_players()}  # Récupère tous les vétos
    remaining = all_choices - vetoes
    group.remaining_choices = ','.join(remaining)
    
def calculate_best_choice(group: Group):
    import random
    remaining_choices = group.remaining_choices.split(',')
    
    if len(remaining_choices) == 1:
                # Si un seul choix reste, c'est automatiquement le meilleur choix
                group.best_choice = remaining_choices[0]
    else:
                # Récupérer les classements des joueurs
                player1 = group.get_players()[0]
                player2 = group.get_players()[1]
    
                choice1_rank = {
                    remaining_choices[0]: (
                        (player1.CHOIX_21 == remaining_choices[0]) +
                        (player2.CHOIX_21 == remaining_choices[0])
                    ),
                    remaining_choices[1]: (
                        (player1.CHOIX_21 == remaining_choices[1]) +
                        (player2.CHOIX_21 == remaining_choices[1])
                    ),
                }
    
                # Comparer les classements pour déterminer le meilleur choix
                if choice1_rank[remaining_choices[0]] > choice1_rank[remaining_choices[1]]:
                    group.best_choice = remaining_choices[0]
                elif choice1_rank[remaining_choices[0]] < choice1_rank[remaining_choices[1]]:
                    group.best_choice = remaining_choices[1]
                else:
                    # En cas d'égalité, tirage au sort
                    group.best_choice = random.choice(remaining_choices)
class Player(BasePlayer):
    CHOIX_1 = models.StringField()
    CHOIX_2 = models.StringField()
    CHOIX_3 = models.StringField()
    Veto_1 = models.StringField()
    CHOIX_21 = models.StringField()
    CHOIX_22 = models.StringField()
def get_choices_of_other_player(player: Player):
    group = player.group
    other_player = player.get_others_in_group()[0]  # Suppose un groupe de deux joueurs
    return {
                'CHOIX_1': other_player.CHOIX_1,
                'CHOIX_2': other_player.CHOIX_2,
                'CHOIX_3': other_player.CHOIX_3,
            }
class Presentation(Page):
    form_model = 'player'
class Choix_honnete(Page):
    form_model = 'player'
    form_fields = ['CHOIX_1', 'CHOIX_2', 'CHOIX_3']
class MyWaitPage(WaitPage):
    pass
class Veto(Page):
    form_model = 'player'
    form_fields = ['Veto_1']
    @staticmethod
    def vars_for_template(player: Player):
        other_choices = get_choices_of_other_player(player)
        return {
                    'CHOIX_1': other_choices['CHOIX_1'],
                    'CHOIX_2': other_choices['CHOIX_2'],
                    'CHOIX_3': other_choices['CHOIX_3'],
                }
class MyWaitPage2(WaitPage):
    after_all_players_arrive = calculate_remaining_choice
class Classement(Page):
    form_model = 'player'
    form_fields = ['CHOIX_21', 'CHOIX_22']
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return {
                    'remaining_choices': group.remaining_choices.split(','),
                }
class MyWaitPage3(WaitPage):
    after_all_players_arrive = calculate_best_choice
class Results(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return {
                    'best_choice': group.best_choice,
                }
page_sequence = [Presentation, Choix_honnete, MyWaitPage, Veto, MyWaitPage2, Classement, MyWaitPage3, Results]