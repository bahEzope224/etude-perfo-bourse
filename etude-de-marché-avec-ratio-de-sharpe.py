#on importe les biblotheques 'yfinance' 'pandas' et 'math'
import yfinance as yf
import pandas
import math


#Liste des symboles de Apple , Microsoft, LVMH, Total, Thalès, Air Liquide, Tesla, ALi Baba
symboles_actions = ['AAPL', 'MSFT', 'MC.PA', 'TTE.PA', 'HO.PA', 'AI.PA', 'TSLA', 'BABA']


#on cree un nouvelle dictionnaire vide appellé 'dico'
dico = {}

#on telecharge les donné avec la fonction yf.download des données des prix des symboles sur les 5 dernières années
data = yf.download(symboles_actions, start='2018-01-01', end='2023-05-01')

#on parcour chaque action 'i' et stocker les prix dans le dictionnaire
for i in symboles_actions:
    dico[i] = data['Adj Close'][i]

print("")
#on affiche les action et leurs prix
print("###########################on affiche les action et leurs prix###########################\n")
print(pandas.DataFrame(dico)) 


#on cree un nouveau dictionnaire 'rendement' pour stocker les rendements journaliers    
rendements = {}

#on Calcule les rendements journaliers pour chaque action
for actions, prix in dico.items():
    #on Calcule les rendements 
    rendements[actions] = (prix / prix.shift(1)) - 1
    #on supprime le premier rendement journalier (le rendement qui est nul)
    rendements[actions] = rendements[actions].iloc[1:]

#on affiche les rendements journalier de chaque action
print("")
print("###########################on affiche les rendements journalier de chaque action###########################\n")
print(pandas.DataFrame(rendements))


#On cree un dictionnaire 'volatilite_ann' pour stocker les volatilités annualisées
volatilite_ann = {}

#On Calcule la volatilité annualisée pour chaque action
for e, retours in rendements.items():
    #On Calculer la volatilité journalière
    volatilite_journaliere = retours.std()
    #On Calcule la volatilité annualisée
    volatilite_ann[e] = volatilite_journaliere * math.sqrt(252)
                                                           
#on cree un index 'index_rendement_ann' qui permettre d'afficher les volatilisées annualisées                  
index_volatilite_ann = pandas.DataFrame(volatilite_ann, index=['Volatilité Annualisée'])

#on affiche la volatilité annualisé
print("")
print("###########################on affiche la volatilité annualisé###########################\n")
print(index_volatilite_ann)


#on cree un dictionnaire pour stocker les rendements cumulé
rendement_cumule = {}

#On calcule le rendement cumulé pour chaque action
for action, prix in dico.items():
    #Calculer le rendement cumulé
    rendement_cumule[action] = (prix.iloc[-1] / prix.iloc[0]) - 1
    
#on cree un index 'index_rendement_cumule' qui permettre d'afficher les rendements cumulés
index_rendement_cumule = pandas.DataFrame(rendement_cumule, index=['Rendements Cumulé'])

#on affiches les rendements cumulisé
print("")
print("###########################on affiches les rendements cumulisé###########################\n")
print(index_rendement_cumule)


#on cree un dictionnaire pour stocker les rendements annualisés
rendement_annualise = {}

#on calculer le rendement annualisé pour chaque action
for action, rendement in rendement_cumule.items():
    #on calcule le rendement annualisé
    rendement_annualise[action] = ((1 + rendement) ** (1/5)) - 1

#on cree un index 'index_rendement_annual' qui permettre d'afficher les rendements annualisé
index_rendement_annual = pandas.DataFrame(rendement_cumule, index=['Rendements Annualisé'])

#on affiche le rendement annualisé
print("")
print("###########################on affiches les rendements anualisé###########################\n")
print(index_rendement_annual)


#on cree un dictionnaire pour stocker les ratios de Sharpe
ratio_sharpe = {}

# Calculer le ratio de Sharpe pour chaque action
for action, rendement in rendement_annualise.items():
    #on suppose que le taux sans risque est de 2%
    taux_sans_risque = 0.02

    #on calcule le ratio de Sharpe avec la formule Ratio de Sharpe = (Rendement de l’actif – Taux sans risque)/Risque total encouru 
    ratio_sharpe[action] = (rendement - taux_sans_risque) / volatilite_ann[action]

#on cree un index 'index_ratio_sharpe' qui permettre d'afficher le ratio de Sharpe  
index_ratio_sharpe = pandas.DataFrame(ratio_sharpe, index=['Ratio de Sharpe'])

#on affiche le ratio de sharpe

print("")
print("###########################on affiches le ratio de sharpe###########################\n")
print(index_ratio_sharpe)


#on extrait les 4 actions avec les meilleurs ratio de Sharpe 
meilleur_ratio_sharpe = sorted(ratio_sharpe.items(), key=lambda x: x[1], reverse=True)[:4]

#on cree une liste des noms des actions recommandées
actions_recommandees = [action[0] for action in meilleur_ratio_sharpe]


#on affiches les actions reccomandés pour l'investissement

print("")
print("###########################on affiches les actions reccomandés pour l'investissement###########################\n")
print("Actions recommandées :")
for action in actions_recommandees:
    print(action)





