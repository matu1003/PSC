"""
Analyse bruteforce du mécansisme hybride

Ce programme a pour objectif de mettre en lumière le fait que le mécanisme hybride est efficace (selon des métriques décrites dans le rapport)
dès lors que les joueurs jouent honnêtement. Pour se faire, on simule tous les comportements possibles pour chaque profil de préférences, le tout itéré un grand
nombre de fois pour lisser le biais aléatoire du choix du mécanisme, et on compare le tout.
"""

from itertools import permutations
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from abc import ABC, abstractmethod
import numpy as np
from scipy.stats import kendalltau


class preference:
    """
    Implémente les profils de préférence des joueurs.

    Attributes:
        pref: [str] -- classement des préférences
        available: {str} -- définit les choix existants
    """


    def __init__(self, classement: list[str]) -> None:
        self.available = {}
        self.available['a'] = 1
        self.available['b'] = 1
        self.available['c'] = 1
        self.available['d'] = 1
        self.available['e'] = 1
        self.pref = []
        if classement != [] : 
            for choix in classement:
                assert choix in self.available
                self.pref.append(choix)

    def __len__(self) -> int:
        return len(self.pref)

    def get_rank(self, choix: str) -> int:
        for i in range(len(self.pref)):
            if self.pref[i] == choix:
                return i + 1
        return -1

    def score_lineaire(self, choix: str) -> int:
        return 6 - self.get_rank(choix)
    



class match:
    """
    Représente une donnée élémentaire, c'est à dire un affrontement entre deux joueurs, munis de leur profil de préférence, avec le résultat de l'affrontement.

    Attributes:
        prof_J1: preference -- préférences du J1
        prof_J2: preference -- préférences du J2
        played_J1: preference -- ce qu'a joué J1. Implémentable via preference selon le formalisme défini pour le mécanisme hybride
        played_J2: preference -- ce qu'a joué J2. Implémentable via preference selon le formalisme défini pour le mécanisme hybride
        result: str
    """

    def __init__(self, J1: preference, J2: preference, PJ1 : preference, PJ2 : preference) -> None:
        self.prof_J1 = J1
        self.prof_J2 = J2
        self.result = "UNDEFINED"
        self.played_J1 = PJ1
        self.played_J2 = PJ2

    def minimum_consensus(self) -> str:
        pass

    def honesty_gap(self, mecanisme: str) -> float:
        if self.result == "UNDEFINED": return 0
        tau1, _ = kendalltau(self.prof_J1.pref, self.played_J1.pref)
        tau2, _ = kendalltau(self.prof_J2.pref, self.played_J2.pref)
        return ((tau1 + 1) / 2, (tau2 + 1) / 2)


    def efficiency_score(self):
        return (self.prof_J1.score_lineaire(self.result) + self.prof_J2.score_lineaire(self.result))
    
    def inequality_score(self):
        return self.prof_J1.score_lineaire(self.result) - self.prof_J2.score_lineaire(self.result)

    def efficiency_max(self):
        max = 0
        for option in ["a", "b", "c", "d", "e"]:
            factice = match(self.prof_J1, self.prof_J2, self.played_J1, self.played_J2)
            factice.result = option
            if factice.efficiency_score() > max:
                max = factice.efficiency_score()
        return max



class dataset: 
    """
    Implémente un ensemble de match associé à un profil donné.

    Attributes:
        - profil: str -- label du profil d'affrontement
        - data: [match] -- données
    """

    def __init__(self, profil: str) -> None:
        self.profil = profil
        self.data = []
    
    def add_data(self, data: match) -> None:
        self.data.append(data)

    
class simulation(ABC):
    """
    Classe abstraite donnant naissance aux classes spécifiques des différents mécanismes. A pour objectif de simuler toutes les possibilités de jeu pour
    une opposition donnée, ainsi que leur résultat et performance associée.

    Attributes:
        dataset_list: [dataset] -- ensemble de dataset, chacun étant associé à un profil d'affrontement
        efficiency_list: [[float]] -- ensemble des données d'efficacité pour chaque match
        honesty_list: [[int]] -- ensemble des données d'honnêteté pour chaque match
        inequality_list[[int]] -- ensemble des données d'inégalité pour chaque match
        max_efficiency:[float] -- A chaque profil d'affrontement, associe l'efficacité maximale


    """

    def __init__(self) -> None:
        ref = preference(["a", "b", "c", "d", "e"])
        prof1 = preference(["e", "d", "c", "b", "a"])
        prof2 = preference(["d", "b", "a", "e", "c"])
        prof3 = preference(["c", "b", "a", "d", "e"])
        prof4 = preference(["e", "c", "a", "b", "d"])
        dataset1 = dataset("profil_1")
        dataset2 = dataset("profil_2")
        dataset3 = dataset("profil_3")
        dataset4 = dataset("profil_4")
        efficiency_data_1 = []
        efficiency_data_2 = []
        efficiency_data_3 = []
        efficiency_data_4 = []
        honesty_data_1 = [[], []]
        honesty_data_2 = [[], []]
        honesty_data_3 = [[], []]
        honesty_data_4 = [[], []]
        inequality_data_1 = []
        inequality_data_2 = []
        inequality_data_3 = []
        inequality_data_4 = []
        self.dataset_list = [dataset1, dataset2, dataset3, dataset4]
        self.efficiency_list = [efficiency_data_1, efficiency_data_2, efficiency_data_3, efficiency_data_4]
        self.honesty_list = [honesty_data_1, honesty_data_2, honesty_data_3, honesty_data_4]
        self.inequality_list = [inequality_data_1, inequality_data_2, inequality_data_3, inequality_data_4]
        played = [list(p) for p in list(permutations(ref.pref))]
        for i in range(len(played)):
            for j in range(len(played)):
                partie1 = match(ref, prof1, preference(played[i]), preference(played[j]))
                partie2 = match(ref, prof2, preference(played[i]), preference(played[j]))
                partie3 = match(ref, prof3, preference(played[i]), preference(played[j]))
                partie4 = match(ref, prof4, preference(played[i]), preference(played[j]))
                dataset1.add_data(partie1)
                dataset2.add_data(partie2)
                dataset3.add_data(partie3)
                dataset4.add_data(partie4)
        self.max_efficiency = []
        self.max_efficiency.append(match(ref, prof1, ref, prof1).efficiency_max())
        self.max_efficiency.append(match(ref, prof2, ref, prof2).efficiency_max())
        self.max_efficiency.append(match(ref, prof3, ref, prof3).efficiency_max())
        self.max_efficiency.append(match(ref, prof4, ref, prof4).efficiency_max())

    @abstractmethod
    def mecanisme(self) -> None:
        """Réalise les affrontements prévus dans le dataset incomplet, auquel il manque les résultats, selon le mécanisme spécifique de la classe.
        """
        pass

    def analysis(self, mecanisme: str) -> None:
        for i in range(4):
            fig, ax = plt.subplots(figsize=(8, 6))
            sc1 = ax.scatter(self.honesty_list[i][0], self.honesty_list[i][1], c=self.efficiency_list[i],alpha = 0.6, cmap='Blues', s=500, edgecolors='k', label = "Efficacité")
            sc2 = ax.scatter(self.honesty_list[i][0], self.honesty_list[i][1], c=self.inequality_list[i], cmap='RdYlGn_r', s=100, edgecolors='k', label = "Inégalité")
            cbar1 = fig.colorbar(sc1, ax=ax, orientation = 'vertical', fraction=0.046, pad=0.1)
            cbar1.set_label("Efficacité")
            divider = make_axes_locatable(ax)
            cax2 = divider.append_axes("right", size="5%", pad=0.7)
            cbar2 = fig.colorbar(sc2, cax=cax2)
            cbar2.set_label('Inégalité')
            ax.set_title("Confrontation de profils " + str(i+1) + " " + mecanisme)
            ax.set_xlabel("Honnêteté joueur 1")
            ax.set_ylabel("Honnêteté joueur 2")
            cax2.text(0.5, 1.03, "avantage au joueur 1", transform=cax2.transAxes, ha='center', va='bottom', fontsize=9)
            cax2.text(0.5, -0.03, "avantage au joueur 2", transform=cax2.transAxes, ha='center', va='top', fontsize=9)
            plt.tight_layout()
            plt.show()
        




class simVR(simulation):
    """
    Simulation de VR.

    Attributes:
        dataset_list: [dataset] -- ensemble de dataset associés à chaque profil d'affrontement
        efficiency_list: [[float]] -- ensemble des données d'efficacité pour chaque match
        honesty_list: [[float]] -- ensemble des données d'honnêteté pour chaque match
        max_efficiency:[float] -- A chaque profil d'affrontement, associe l'efficacité maximale
    """

    def __init__(self) -> None:
        super().__init__()

    
    def mecanisme(self):
        for i in range (len(self.dataset_list)):
            for partie in self.dataset_list[i].data:
                non_veto = []
                for option in ["a", "b", "c", "d", "e"]:
                    if option != partie.played_J1.pref[3] and partie.played_J1.pref[4] and partie.played_J2.pref[3] and partie.played_J2.pref[4]:
                        non_veto.append(option)
                mieux_classe = [non_veto[0]]
                score_cumul_min = partie.played_J1.get_rank(non_veto[0]) + partie.played_J2.get_rank(non_veto[0])
                for option in non_veto:
                    score_cumul = partie.played_J1.get_rank(option) + partie.played_J2.get_rank(option)
                    if score_cumul < score_cumul_min:
                        mieux_classe = [option]
                    elif score_cumul == score_cumul_min:
                        mieux_classe.append(option)
                partie.result = np.random.choice(np.array(mieux_classe))
                self.efficiency_list[i].append(partie.efficiency_score())
                self.honesty_list[i][0].append(partie.honesty_gap("VR")[0])
                self.honesty_list[i][1].append(partie.honesty_gap("VR")[1])
                self.inequality_list[i].append(partie.inequality_score())
    
class simSL(simulation):
    """Simulation de SL
    
    Attributes:
        dataset_list: [dataset] -- ensemble de dataset associés à chaque profil d'affrontement
        efficiency_list: [[float]] -- ensemble des données d'efficacité pour chaque match
        honesty_list: [[float]] -- ensemble des données d'honnêteté pour chaque match
        max_efficiency:[float] -- A chaque profil d'affrontement, associe l'efficacité maximale
    """

    def __init__(self) -> None:
        super().__init__()
        ref = preference(["a", "b", "c", "d", "e"])
        prof1 = preference(["e", "d", "c", "b", "a"])
        prof2 = preference(["d", "b", "a", "e", "c"])
        prof3 = preference(["c", "b", "a", "d", "e"])
        prof4 = preference(["e", "c", "a", "b", "d"])
        played = [list(p) for p in list(permutations(ref.pref))]
        for i in range(len(played)):
            for j in range(len(played)):
                partie1 = match(prof1, ref, preference(played[i]), preference(played[j]))
                partie2 = match(prof2, ref, preference(played[i]), preference(played[j]))
                partie3 = match(prof3, ref, preference(played[i]), preference(played[j]))
                partie4 = match(prof4, ref, preference(played[i]), preference(played[j]))
                self.dataset_list[0].add_data(partie1)
                self.dataset_list[1].add_data(partie2)
                self.dataset_list[2].add_data(partie3)
                self.dataset_list[3].add_data(partie4)

    def mecanisme(self) -> None:
        for i in range(len(self.dataset_list)):
            for partie in self.dataset_list[i].data:
                shortlist = partie.played_J1.pref[:2].copy()
                choix = shortlist[0]
                for j in range(1, 3):
                    if partie.played_J2.get_rank(partie.played_J1.pref[j]) < partie.played_J2.get_rank(choix):
                        choix = partie.played_J1.pref[j]
                partie.result = choix
                self.efficiency_list[i].append(partie.efficiency_score())
                self.honesty_list[i][0].append(partie.honesty_gap("SL1")[0])
                self.honesty_list[i][1].append(partie.honesty_gap("SL1")[1])
                self.inequality_list[i].append(partie.inequality_score())

class hybride(simulation):
    """
    Simulation du mécanisme hybride.

    Attributes:
        dataset_list: [dataset] -- ensemble de dataset associés à chaque profil d'affrontement
        efficiency_list: [[float]] -- ensemble des données d'efficacité pour chaque match
        honesty_list: [[float]] -- ensemble des données d'honnêteté pour chaque match
        max_efficiency:[float] -- A chaque profil d'affrontement, associe l'efficacité maximale
    """

    def __init__(self) -> None:
        super().__init__()

    def mecanisme(self) -> None:
        for i in range(len(self.dataset_list)):
            for partie in self.dataset_list[i].data:
                mec = np.random.choice(["VR", "SL1", "SL2"], p=[0.5, 0.25, 0.25])
                if mec == "VR":
                    non_veto = []
                    for option in ["a", "b", "c", "d", "e"]:
                        if option != partie.played_J1.pref[3] and partie.played_J1.pref[4] and partie.played_J2.pref[3] and partie.played_J2.pref[4]:
                            non_veto.append(option)
                    mieux_classe = [non_veto[0]]
                    score_cumul_min = partie.played_J1.get_rank(non_veto[0]) + partie.played_J2.get_rank(non_veto[0])
                    for option in non_veto:
                        score_cumul = partie.played_J1.get_rank(option) + partie.played_J2.get_rank(option)
                        if score_cumul < score_cumul_min:
                            mieux_classe = [option]
                        elif score_cumul == score_cumul_min:
                            mieux_classe.append(option)
                    partie.result = np.random.choice(np.array(mieux_classe))
                elif mec == "SL1":
                    shortlist = partie.played_J1.pref[:2].copy()
                    choix = shortlist[0]
                    for j in range(1, 3):
                        if partie.played_J2.get_rank(partie.played_J1.pref[j]) < partie.played_J2.get_rank(choix):
                            choix = partie.played_J1.pref[j]
                    partie.result = choix
                else:
                    shortlist = partie.played_J2.pref[:2].copy()
                    choix = shortlist[0]
                    for j in range(1, 3):
                        if partie.played_J1.get_rank(partie.played_J2.pref[j]) < partie.played_J1.get_rank(choix):
                            choix = partie.played_J2.pref[j]
                    partie.result = choix
                self.efficiency_list[i].append(partie.efficiency_score())
                self.honesty_list[i][0].append(partie.honesty_gap(mec)[0])
                self.honesty_list[i][1].append(partie.honesty_gap(mec)[1])
                self.inequality_list[i].append(partie.inequality_score())



def main():
    testVR = simVR()
    testVR.mecanisme()
    testVR.analysis("VR")
    testSL = simSL()
    testSL.mecanisme()
    testSL.analysis("SL")
    testHybrid = hybride()
    testHybrid.mecanisme()
    efficiency_avg_list = [testHybrid.efficiency_list]
    honesty_avg_list = [testHybrid.honesty_list]
    inequality_avg_list = [testHybrid.inequality_list]
    nb_avg = 10
    for _ in range(nb_avg):
        testH = hybride()
        testH.mecanisme()
        efficiency_avg_list.append(testH.efficiency_list)
        honesty_avg_list.append(testH.honesty_list)
        inequality_avg_list.append(testH.inequality_list)
    honesty_avg = []
    efficiency_avg = []
    inequality_avg = []
    for i in range(4):
        honesty_avg_i = [[], []]
        efficiency_avg_i = []
        inequality_avg_i = []
        for j in range(len(testHybrid.honesty_list[0][0])):
            h_value = [0, 0]
            e_value = 0
            i_value = 0
            for k in range(nb_avg):
                h_value[0] += honesty_avg_list[k][i][0][j]
                h_value[1] += honesty_avg_list[k][i][1][j]
                e_value += efficiency_avg_list[k][i][j]
                i_value += inequality_avg_list[k][i][j]
            h_value[0] /= nb_avg
            h_value[1] /= nb_avg
            e_value /= nb_avg
            i_value /= nb_avg
            honesty_avg_i[0].append(h_value[0])
            honesty_avg_i[1].append(h_value[1])
            efficiency_avg_i.append(e_value)
            inequality_avg_i.append(i_value)
        honesty_avg.append(honesty_avg_i)
        inequality_avg.append(inequality_avg_i)
        efficiency_avg.append(efficiency_avg_i)
    testHybrid.efficiency_list = efficiency_avg
    testHybrid.honesty_list = honesty_avg
    testHybrid.inequality_list = inequality_avg
    testHybrid.analysis("Hybride")



if __name__ == "__main__":
    main()