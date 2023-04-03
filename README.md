# -----------Présentation rapide du Projet ------------------

- Dans le cadre d'un projet mémoire de fin de formation MLOPS, nous avons récupéré le développement
d'un ancien projet réalisé en formation Data Scientist sur la réalisation de modèles IA d'analyse de 
sentiments.
- Le but n'étant pas d'optimiser ces modèles, mais plutôt de réaliser un ensemble de méthodes de mise 
en production selon le cycle de vie MLOps.
- Nous avons retenu 3 modèles sur 8 testés auparavant : 1 Gradient Boosting Classifier, 1 Support Vector Machine
 et un Artificial Neuronal Network tous 2 lancés après un modèle pré-entrainé wikipedia2vec


# ------------ Lancement de ce REPO Github ------------------

## sur un IDE (VSC par exemple) en local
 - $ git clone https://github.com/egasnier/mlops_projet2.git  
    => cela va copier tous les dossier et fichiers du REPO dans un nouveau dossier local "mlops_projet2"

## récupérer wikipedia2vec
- ce modèle pré-entrainé de wikipedia étant assez lourd (+ de 1Go), nous ne pouvons le déposer sur GitHub.
Aussi, veuillez suivre ce lien pour le télécharger en local et placer ce fichier dans le dossier /airflow/clean_model
Ceci est obligatoire et doit être réalisé après la copie du repo en local sur votre machine.
- Voici le lien où récupérer le modèle pré-entrainé trained.pickle :
https://drive.google.com/file/d/1v38YH0El-jEYUoWQ1spY4Upc5DSDVLSj/view?usp=share_link

# ---- voir les navigateurs FastApi et Streamlit tourner ----
## A : Création des containers FastApi et Streamlit
 - $ cd mlops_projet2  # se placer sur le dossier de travail du repo
 - $ docker network create AIservice  # créer le reseau AIservice
 - $ docker network ls   # vérification
 - $ docker-compose up -d --build  # création des images et lancement des containers fastapi et streamlit
    => cela peut prendre entre 5 à 10 minutes la 1ere fois selon le PC

ATTENTION : si votre PC n'a pas plus de 16Go de RAM, cela peut être délicat pour la suite.
aussi nous mettons à votre disposition les images déjà construites et informations nécessaire en partie D. REMARQUES

## B : voir la console FastAPI sur un navigateur
- aller sur http://localhost:8000/docs

## C :  voir la console Streamlit sur un navigateur
- aller sur http://localhost:8501

## D : Création des containers Airflow ( 7 containers ici)
- $ cd airflow   # se placer sur le sous-dossier /airflow
- $ docker-compose up -d --build  # création des images et lancement des containers airflow

REMARQUES : Nous n'avons pas utilisé d'images alpine dès le début dans notre projet, d'où un poids important des images crées
et une utilisation de ressources RAM importante. Devant rendre le projet rapidement maintenant, nous vous proposons de
récupérer les images contruites et déposées sur DockerHub (créez un compte si besoin).

- il vous faudra alors modifier les codes des docker-compose en remplaçant 
build : /fastapi    par    image: fredzang/my_fastapi_mlops:2.0.0     # dans le docker-compose principal
build : /streamlit  par    image: fredzang/my_streamlit_mlops:2.0.0   # dans le docker-compose principal
build: .   par   image: ${AIRFLOW_IMAGE_NAME:fredzang/my_airflow_mlops:2.0.0}  # dans le docker-compose de airflow

- le lancement des containers se fait dans ce cas avec la commande :
- $ docker-compose up -d    # au lieu de  docker-compose up -d --build

## E : voir la console Airflow sur un navigateur
- aller sur http://localhost:8080
- login et password = airflow

## F : par la suite
- une fois toutes ces étapes réalisées, ce sera bien plus simple par la suite :
Il vous suffira de lancer les 2 docker-compose pour relancer tous les containers et accéder aux consoles sur votre navigateur,
avec un bien meilleur délai de construction

# --------------- Arborescence et Fonctionnement ----------

## Gestion de nos bases de Données
- N'ayant pas accès à l'API des données, nous avons reçu une base de 17200 lignes que nous avons découpée en 3 parties
pour simuler les mises-à-jour de notre base de données, des modélisations et reporting selon des métriques et exigences
de performances que nous avons définis.

- Ainsi, Fastapi gère notre base de données, sa mise-à-jour par ajout d'un fichier csv de nouvelles données
et la possibilité d'ajouter un commentaire et sa notation directement à data_MAJ.csv qui est la base de référence
actualisée et utilisée par Streamlit et Airflow par la suite.

- Streamlit nous sert de Présentation détaillée du projet, des Problématiques rencontrées et Améliorations à prévoir,
de Prédiction à la demande, Visual Reporting et Alertes Performances de chacun.

- Airflow nous sert de pipeline CI/CD afin de réaliser les preprocessings, les training et reporting de nos 3 modèles.
Les modèles mis-à-jour sont sauvegardés avec date et heure de réalisation dans /airflow/clean_model
Les reportings mis-à-jour sont sauvegardés avec date et heure de réalisation dans /airlow/clean_data

# --------------- Test général que vous pouvez réaliser ------
- 1 : une fois tous le containers lancés, déclenchez le DAG Airflow manuellement : la 1ere base de donnée data_MAJ.csv sera chargée et la réalisation
des différentes tâches se réalise en 3 minutes (selon votre PC). Puis les fichiers de mises-à-jour des modèles apparaitront dans le dossier local clean_models (après 1 minute, le temps de passer des volumes de containers à votre local). Les fichiers de reporting horodatés seront disponibles dans le dossier clean_data.
- 2 : passer ensuite sur le navigateur FastAPI, au endpoint /uploadfile ( se connecter en username = admin avec password = admin), et choisissez le fichier new_data_test_1.csv dans le sous-dossier /airflow/clean_data/--new_data_test. Exécutez le chargement et ce fichier se rajoutera à la base de données initiale data_MAJ.csv
- 3 : Déclencher à nouveau le DAG dans le navigateur Airflow et le processus de mise-à-jour se répète en 6 minutes à présent.
- 4 : Charger le dernier fichier de data nommé new_data_test_2.csv par le navigateur FastAPI
- 5 : Déclencher une dernière fois le DAG via Airflow, ce qui prend bien 10 minutes cette fois-ci.
- 6 : Enfin, sur le navigateur Streamlit, vous pourrez constater, en rafraichissant la page "Reporting et Alerte Exigences", les performances et évolutions de chaque modèle après chaque mise-à-jour.

# ----------- Nous aurions aimé faire bien plus -------------
- Nous aurions aimé avoir plus de temps pour optimiser notre code et le transférer sur un Cloud pour simplifier la procédure d'installation.
La formation MLOps de DataScientest est très dense avec de nombreux examens pour valider les modules d'apprentissage.
Il nous fallait atteindre le dernier module pour avoir enfin une vue d'ensemble et réaliser ce projet en 2 semaines
intenses, mais ce fût un vrai plaisir dans le partage, la découverte de nombreux autres concepts pour lever bien des bugs
et la mise en pratique de notre 1er projet MLOps.
- Nous avons dédié une page "Améliorations à prévoir et problématiques" dans notre Streamlit pour les plus curieux. Une page "Modélisation à la demande" est aussi disponible
pour tester en direct les prédictions de chaque modèle selon la mise à jour réalisée.
- Pour finir, nous tenons à remercier Alban et toute l'équipe de DataScientest pour cette belle et enrichissante formation.

Quan, Éric & Fred, la Satispy Team ;-)
