# Documentation
"""
Created on Wed Jan 15 15:43:08 2025
@author: jerome.hertzog_squar
*- coding: utf-8 -*
"""

## Directory
- Overpass /
	- <u>fichiers en sortie</u> : résultats-comparatifs /
	- <u>fichiers en entrée</u> : csv /
		- main.csv : comprend toutes les entreprises testées lors
		des tests
		- CAC40.csv
		- etatsunis.csv : pour les Etats-Unis
		- uk.csv : angleterre
		- 5entreprises : 5 petites entreprises en plus pour
		ajouter des tests
	- json / > on stocke les résultats des requêtes


## FLAGS : 
	Variations possibles pour un nom d'entreprise
0. Nom de base écrit dans le fichier CSV
1. Tout en majuscule
2. Tout en minuscule
3. Première lettre majuscule
### Caractères de séparation
	- " "
	- "-"
	- "_"
### Si caractère de séparation trouvé
- On supprime le caractère trouvé -> devient notre "espace"

- On remplace l'"espace" par un caractère de séparation présent dans la liste (de taille 3), et après le remplacement :
	5. Tout en majuscule
	6. Tout en minuscule
	7. Première lettre majuscule
- On remplace l'"espace" par le deuxième caractère de séparation de la liste des caractères
	8. Tout en majuscule
	9. Tout en minuscule
	10. Première lettre majuscule

## Pour faire tourner le code
Deux options s'offrent à l'utilisateur : 
Taper 1 ou 2 en fonction du choix.
1. Générer un fichier CSV depuis un autre fichier CSV.
2. Générer un fichier CSV depuis une seule entreprise.

### Déroulement de l'option 1
- Rentrer un nom d'entreprise (le programme va au final générer un fichier CSV avec cette entreprise).
- Pour chaque manière d'écrire le nom :
	- Initialisation de la requête Overpass avec le nom actuel
	- On ajoute les données au dictionnaire Python regroupant tous les résultats
- On convertit le dictionnaire en fichier CSV

### Déroulement de l'option 2
- On ouvre un fichier CSV au début du programme, et on va lire chaque ligne à partir de la deuxième (car on ne veut pas prendre en compte le nom de la colonne).
- Pour chaque ligne récupérée, cela va correspondre à l'option 1

### Contraintes
- Le dossier de destination doit exister
- On ne peut réaliser que 10.000 requêtes par jour

## Code : partie tests
Cette partie de la documentation concerne le fichier \testsCoordonnees.py
On parcourt un fichier CSV et on récupère toutes les données. Dans le même temps, on prend les coordonnées de chaque nœud et on va lancer 2 requêtes HTTP : 
* une sur Google Maps : 
Exemple : https://www.google.com/maps/place/11.3307057,-12.2824692/@11.3307057,-12.2824692,15z
* et une sur Notminatim
	coordonnees_api = "Lat,Long"
	Exemple : https://nominatim.openstreetmap.org/ui/search.html?q=11.3307057,-12.2824692
* On ouvre 1 page pour chaque URL sur Chrome
	* Pour chaque occurrence :
		* Input : 
			* Touche "Entrée" directement-> 1 : bonne précision
			* Ecrire 0 et touche "Entrée" : mauvaise précision
			* Ecrire 2 et touche "Entrée" : "peut-être
			* Ecrire exit et touche "Entrée" : sortir de la fonction
		* Si Input = "exit"
			* On vérifie si le dictionnaire que l'on veut créer contient bien des valeurs, et s'il en contient :
				* On crée un dictionnaire avec les valeurs trouvées, et on génère une nouvelle DataFrame avec ce dictionnaire
				* Si le fichier existe, on ajoute les nouvelles valeurs au fichier en sortie
				* Sinon, on crée un nouveau fichier à partir de la DataFrame
				* Enfin, on regarde s'il n'y a pas de doublon, auquel cas on les supprime
			* On "casse" la boucle
		* Sinon on affecte un coefficient de précision correspondant au taux de précision renseigné par Input
		* Ensuite il y a la possibilité de rentrer un commentaire pour indiquer ce qui ne va pas
		* Et on ajoute les données de l'occurrence à des listes contenant les informations dont on a besoin, une par tag.
* Dès que l'on a fini le programme (sous 2 possibilités) :
	* Exit
	* On a fait 500 occurrences
		* On ferme les onglets
- 