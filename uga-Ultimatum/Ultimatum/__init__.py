
from otree.api import *
c = "$"
rewards_reject = [[0,0], [0, 100], [100, 0]]
doc = ''
class C(BaseConstants):
    NAME_IN_URL = 'Ultimatum'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 3
    POT = 100
    PROPOSANT_ROLE = 'Proposant'
    ACCEPTANT_ROLE = 'Acceptant'

class Subsession(BaseSubsession):
    pass

def creating_session(subsession: Subsession):
    session = subsession.session
    subsession.group_randomly()

def shuffle(subsession: Subsession):
    session = subsession.session
    subsession.group_randomly()


class Group(BaseGroup):
    pass
class Player(BasePlayer):
    offre = models.CurrencyField(max=C.POT, min=0)
    accepter = models.BooleanField()
class Presentation(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player: Player):
        session = player.session
        subsession = player.subsession
        return subsession.round_number == 1
class Jeu(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        session = player.session
        subsession = player.subsession
        rewards = rewards_reject[subsession.round_number-1]
        return {"Round": subsession.round_number, "pone": rewards[0], "ptwo": rewards[1]}

class Offre(Page):
    form_model = 'player'
    form_fields = ['offre']
    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.PROPOSANT_ROLE
class WaitOffre(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.ACCEPTANT_ROLE
class Decision(Page):
    form_model = 'player'
    form_fields = ['accepter']
    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.ACCEPTANT_ROLE
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return {"offre": group.get_player_by_role("Proposant").offre}
class WaitAccept(WaitPage):
    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.PROPOSANT_ROLE
class RESULT(Page):
    form_model = 'player'
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        subsession = player.subsession
        rewards = rewards_reject[subsession.round_number-1]

        if group.get_player_by_role(C.ACCEPTANT_ROLE).accepter:
            offre = group.get_player_by_role(C.PROPOSANT_ROLE).offre
            if player.role == C.PROPOSANT_ROLE:
                player.payoff = C.POT - offre
            else:
                player.payoff = offre
        else:
            player.payoff = rewards[player.id_in_group-1]
        return {"gains": player.payoff}
class MyWaitPage(WaitPage):
    wait_for_all_groups = True
page_sequence = [Presentation, Jeu, Offre, WaitOffre, Decision, WaitAccept, RESULT, MyWaitPage]
