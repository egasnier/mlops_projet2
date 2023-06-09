# CHARGEMENT DES PACKAGES
import numpy as np
import pandas as pd
import pickle
import re
import spacy
import os

from sklearn.model_selection import train_test_split


# PRETRAITEMENT DES DONNEES - TRANSFORMATION DES ETOILES EN CIBLE (0 ou 1)
def transform_star_to_target(df_comment):
    """Transforme les étoiles en cible:
            1 ou 2 étoiles    => Sentiment négatif (0)
            3, 4 ou 5 étoiles => Sentiment positif (1)

    Parameters:
    -----------
        df_comment : DataFrame contenant les commentaires (str)

    Returns:
    --------
        Liste contenant des entiers (0 ou 1)
    """
    new_star = {1: 0, 2: 0, 3: 1, 4: 1, 5: 1}
    df_comment.star.replace(new_star, inplace=True)
    return df_comment.star.astype('int')

# FONCTION token_lemmatiser() DE PRETRAITEMENT => question : est ce que le
# csv sauvegardé est utile ?


def token_lemmatiser(path, save_path='/app/clean_data/data_preprocess_v1.csv'):
    """ Traitement des données origines afin d'avoir des commentaires nettoyées
            1. Selon l'analyse: 'r a s ' ou  ' r à s' ou 'r à d' ou 'r a d' et convertir en 'bien'
                            +  'ras le bol' convertir en 'mauvaise
            2. Tokenisation
            3. Elimination des tokens vides
            4. Lemmatisation des mots francais
            5. Retirer les tokens de moins de 2 lettre
            6. Traitement des mots vides (avec liste_no-stop-words_tokens_unique.xlsx )
            7. Sauvegarder le ficher sous nom: review_trust_fr_lemmantiser_word+2_VF.csv
    Parameters:
    -----------
        path : Chemin pour accéder au fichier csv (données origines)
        save_path : Chemin pour sauvegarder le ficher csv (données nettoyées)
    Returns:
    --------
        Un fiche .csv
    """
    # chargement fichier csv (données origines)
    data = pd.read_csv(path, sep=',')
    data.drop(data.iloc[:, :1], axis=1, inplace=True)

    # remplacer les stars 1,2 => 0 et 3,4,5 => 1 par function
    # transform_star_to_target()
    new_star = {1: 0, 2: 0, 3: 1, 4: 1, 5: 1}
    data.star.replace(new_star, inplace=True)

    # # récupérer colonne 'Commentaire' sous forme de liste de str dans corpus
    corpus = data['Commentaire'].tolist()

    # les 4 regex vus ci-dessus rappelés ici
    # pb r.a.s, r.à.s, r.a.d et r.à.d
    re_ras_points = re.compile(r"(r.a.s)|(r.à.s)|(r.a.d)|(r.à.d)")
    # pb r a s , r a d , r à s , r à d
    re_r_a_s = re.compile(r"[r]+[\s]+[a|à]+[\s]+[s|d]$")
    # pb ras , rad , ràs , ràs
    re_ras = re.compile(r"\bras\b|\bràs\b|\brad\b|\bràd\b")
    re_raslebol = re.compile(r"(ras le bol)+")                # pb ras le bol

    corpus_ras_le_bol = []
    for ele in corpus:
        result = re_raslebol.sub('mauvais', ele)
        corpus_ras_le_bol.append(result)

    # trouver les 'r.a.s' ou 'r.à.s' ou 'r.a.d' ou 'r.à.d' et convertir en
    # 'bien'
    corpus_ras = []
    for ele in corpus_ras_le_bol:                          # list_test remplacé par corpus pour test     OK BON
        result = re_ras_points.sub('bien', ele)
        corpus_ras.append(result)

    # trouver les 'r a s ' ou  ' r à s' ou 'r à d' ou 'r a d' et convertir en
    # 'bien'
    corpus_ras2 = []
    for ele in corpus_ras:                          # list_test remplacé par corpus pour test     OK BON
        result = re_r_a_s.sub('bien', ele)
        corpus_ras2.append(result)

    # trouver les 'ras' ou 'ràs' ou 'rad' ou 'ràd' et convertir en 'bien'
    corpus_ras3 = []
    for ele in corpus_ras2:                          # list_test remplacé par corpus pour test     OK BON
        result = re_ras.sub('bien', ele)
        corpus_ras3.append(result)

    # remplacement 'ras',  'r a s' et 'ras le bol' terminé à ce stade  ET commentaires traités placés dans 'corpus_ras3'
    # bascule du traitement dans corpus
    corpus = corpus_ras3

    # Tokenisation corpus_tk¶
    # stop ponctuations, nombres et smileys et liste de mots en laissant tous les accents et lettres spéciales minuscules
    # compiler et création liste de liste de token dans corpus_tk

    re_token = re.compile(r"[^a-zéèêàâîïàùçôëûæœ]+")
    corpus_tk = []
    for line in corpus:
        corpus_tk.append(re_token.split(line))

    # ajout colonne token à data
    data['tokens'] = pd.Series(corpus_tk)
    #  décompte des token
    total = []
    for i in range(data.shape[0]):
        total.append(len(data['tokens'][i]))

    # ajout de la colonne du total des tokens restants
    data['total1'] = total

    # élimination des token vides créés après tokenisation à cause des ! ! !
    # par exemple
    clean_tk = []
    for row_list in corpus_tk:
        clean_tk.append([ele for ele in row_list if len(ele) != 0])

    # verif total token restant
    serie_clean_tk = pd.Series(clean_tk)
    #  décompte des token
    total = []
    for i in range(data.shape[0]):
        total.append(len(serie_clean_tk[i]))

    # pas de nouvelle colonne crée dans data donc réafectation de clean_tk
    # dans corpus_tk
    corpus_tk = clean_tk

    # Lemmatisation des mots Français
    # test lemmatisation avant lancement sur corpus

    # utilisation du module spacy importé
    nlp = spacy.load('fr_core_news_md')
    # Lemmatisation sur vrai data_set corpus_mot

    corpus_lem = []
    for line_com in corpus_tk:
        liste = []
        doc = nlp(" ".join(line_com))
        for token in doc:
            liste.append(token.lemma_)
        corpus_lem.append(liste)

    data['lemmatiser'] = pd.Series(corpus_lem)
    #  décompte des token
    total = []
    for i in range(data.shape[0]):
        total.append(len(data['lemmatiser'][i]))
    # ajout de la colonne du total des mots lemmentisés
    data['tot_lem'] = total

    # retirer les tokens de moins de 2 lettres
    corpus_sw = [[mot for mot in line_com if len(
        mot) > 2] for line_com in corpus_lem]
    # ajouter colonne résultat à data
    corpus_sw_serie = pd.Series(corpus_sw)
    data['words+2'] = corpus_sw_serie
    #  décompte des tokens restants
    total = []
    for i in range(data.shape[0]):
        total.append(len(data['words+2'][i]))
    # ajout de la colonne du total des tokens restants
    data['tot_+2'] = total

    # traitement des mots vides #
    # chargement fichier excel de stop words french en dataframe
    df_stop_word_xls = pd.read_excel(
        '/app/clean_data/liste_no-stop-words_tokens_unique.xlsx',
        header=None)

    # création de stop words set

    # faire une liste selon nltk.corpus
    update_list_fr = list(df_stop_word_xls[0])

    # initialisation de la variable des mots vides
    stop_words = set()
    stop_words.update(update_list_fr)

    # fonction de filtrage
    def stop_words_filtering(mots, stop_words):
        tokens = []
        for mot in mots:
            if mot not in stop_words:
                tokens.append(mot)
        return tokens

    # création des tokens filtrés par stop_words.update et ajout de la colonne
    # créé
    data['no_stop_words'] = data['words+2'].apply(
        lambda x: stop_words_filtering(
            x, stop_words))   # ok parfait

    #  décompte des tokens no_stop_word
    total = []
    for i in range(data.shape[0]):
        total.append(len(data['no_stop_words'][i]))

    # ajout de la colonne du total des tokens restants
    data['tot_sw'] = total

    # sauvegarder le dataframe sous csv
    df_cleaned = data.drop(['total1', 'tot_lem', 'tot_+2', 'tot_sw'], axis=1)
    df_cleaned.to_csv(save_path)

    return df_cleaned


# TRAITEMENT DES MOTS VIDES (ou STOP WORDS)
def collect_stopwords(path):
    """Collecte des stopwords stockés dans un fichier Excel

    Parameters:
    -----------
        path : Chemin pour accéder au fichier Excel

    Returns:
    --------
        set de mots vides (ou stop words)
        (a set is a collection of unique data)
    """
    # Chargement fichier excel de stop words french en dataframe
    df_stop_word_xls = pd.read_excel(path, header=None)

    # Création de stop words set
    # Liste selon le retour d'expérience projet
    update_list_fr = list(df_stop_word_xls[0])

    # Initialisation de la variable des mots vides
    stop_words = set()
    stop_words.update(update_list_fr)
    return stop_words


# MODELE PREENTRAINE AVEC WIKIPEDIA - SIMILARITES DE MOTS
def find_similar(path_model_wiki, positive, negative):
    """_summary_

    Args:
    -----
        path_model_wiki (str): Chemin du modèle Wikipedia ('../data/Modeles/trained.pickle')
        positive (list of str): Liste de mots (Ex: ['roi', 'femme'])
        negative (list of str): Liste de mots (Ex: ['homme'])

    Returns:
    --------
        Le mot le plus probable avec les similarités positives et négatives (Ex: 'reine')
    """
    # charger le modèle pré-entrainé sauvegardé
    trained = pickle.load(open(path_model_wiki, 'rb'))

    # exemple commun de test calculatoire sur les token : +A - C => +B - ?
    # avec A=roi, C = homme, B=femme => ? = reine solution
    return trained.most_similar(positive=positive, negative=negative)[0][0]


# FONCTION my_doc2vec() DE PRETRAITEMENT
def my_doc2vec(doc, trained):
    """Fonction pour transformer un document (ici une ligne de commentaire) en vecteur à partir des tokens qui le compose

    Parameters:
    -----------
        doc (str): lignes de commentaires à traiter
        trained (.pickle): modèle pré-entrainé sur wikipedia

    Returns:
        Vecteur représentant le document (vecteur nul si aucun token trouvé)
    """

    # Dimension de représentation
    p = trained.vectors.shape[1]   # p = 100
    # Intitialisation du vecteur
    vec = np.zeros(p)  # array (100,)
    # Initialisation du nombre de tokens trouvés à 0
    nb = 0
    # Traitement de chaque token de la ligne de commentaire
    for tk in doc:
        # ne traiter que les tokens reconnus
        try:
            values = trained[tk]  # on récupère le vecteur du token concerné
            vec = vec + values   # on incrémente ce vecteur dans vec
            nb = nb + 1.0        # le compteur de token d'incrémente
        except BaseException:
            pass  # pour lever l'erreur si aucun token trouvé dans notre modele pré-entrainé
        # moyenne des valeurs uniquement si on a des tokens reconnus
    if (nb > 0.0):
        vec = vec / nb
    return vec  # renvoie le vecteur moyenné ou un vecteur nul si aucun token trouvé


# PRETRAITEMENT DU CORPUS ET CREATION DES JEUX D'ENTRAINEMENT ET DE TEST
# POUR LES MODELES SVM ET ANN
def prepare_data(path_data, path_model_wiki):
    """Prétraitement du corpus afin de fournir les jeux d'entrainement et de test

    Args:
    -----
        path_data (str): Chemin de stockage des données nétoyées ('../data/review_trust_fr_lemmantiser_word+2_VF.csv')
        path_model_wiki (str): Chemin du modèle Wikipedia ('../data/Modeles/trained.pickle')

    Returns:
    --------
        X_train, X_test, y_train, y_test: Jeux d'entrainement et de test
    """

    # Charger le modèle pré-entrainé sauvegardé
    trained = pickle.load(open(path_model_wiki, 'rb'))

    # Importer les données nettoyées
    data = pd.read_csv(path_data, sep=',')
    data.drop(data.iloc[:, :1], axis=1, inplace=True)
    # data.sample(1)

    # Préparer la liste corpus_sw pour modèle
    corpus_sw = data['no_stop_words'].tolist()
    # corpus_sw = data['words+3'].tolist()

    # Traiter les documents du corpus
    docsVec = list()
    # Pour chaque ligne du corpus nettoyé
    for doc in corpus_sw:
        # calculer son vecteur
        vec = my_doc2vec(doc, trained)
        # ajouter dans la liste
        docsVec.append(vec)

    # Transformer en array numpy
    matVec = np.array(docsVec)

    # Transformer en dataframe
    X = pd.DataFrame(matVec, columns=["v" + str(i + 1)
                     for i in range(matVec.shape[1])])

    # Récupération de la cible
    y = data.star

    # Partition en train_set et test_set
    return train_test_split(X, y, test_size=0.2, random_state=20)


# REPORTING - PERFORMANCES
def save_report(classif, time, data_store_path, data_name):
    """Sauvegarde des données du rapport de classification (f1-score et accuracy)

    Args:
    -----
        classif: rapport de classification au format dict
        time: date-heure
        data_store_path: répertoire dans lequel les rapports sont enregistrés
        data_name = nom du fichier de sauvegarde sans l'extension .csv

    Returns:
    --------
        None
    """
    # Collecte des nouvelles données du rapport de classification
    df_classif = pd.DataFrame(classif)
    new_row = pd.DataFrame(data=[[time,
                                  df_classif.loc['f1-score', '0'],
                                  df_classif.loc['f1-score', '1'],
                                  df_classif.loc['f1-score', 'accuracy']]],
                           columns=['Date-Heure', 'f1_0', 'f1_1', 'accuracy'])

    # SAUVEGARDE CLASSIFICATION_REPORT
    # nommage des chemins
    data_type = '.csv'

    # chemin et nom du fichier à sauvegarder
    data_file = data_store_path + data_name + data_type

    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        df = pd.concat([df, new_row], axis=0, ignore_index=True)
        df.to_csv(data_file, index=False)
    else:
        df = pd.DataFrame(columns=['Date-Heure', 'f1_0', 'f1_1', 'accuracy'])
        df = pd.concat([df, new_row], axis=0, ignore_index=True)
        df.to_csv(data_file, index=False)
