# Nakalator

![python-versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C3.11-blue)

Nakalator est un CLI pour faciliter la création de dépôt et l'envoi de fichiers sur la plateforme [Nakala](https://nakala.fr/).

Nakalator permet : 

- de créer un dépôt sur Nakala avec des métadonnées associées grâce à un fichier YAML ;
- d'envoyer des fichiers (par exemple, des images) sur Nakala associé à une donnée ;
- de créer une collection de données ou de rattacher des données à une collection existante dans Nakala;

Il peut-être conçu comme une alternative à l'outil [Mynkl](https://mynkl.huma-num.fr/). 

Les avantages de Nakalator sont les suivants :

- **Retour utilisateur** : permet de tracer le nombre de fichiers envoyées sur Nakala en cours d'envoi ; 
- **Performances** : suivant le type de machine utilisé et la quantité de fichiers, Nakalator réduit le temps d'envoi des fichiers sur Nakala via une méthode d'envoi **multi-threads** (go routines) ;
- **Intégrité des données envoyées** : génération d'un fichier de *mapping* des fichiers envoyées sur Nakala avec les identifiants DOI et sha1 à la fin de la procédure et réalisation de tests automatiques de vérification après l'envoi des fichiers.

Par défaut, les données et les collections créées dans Nakala sont en mode privées ou en attente.

----

## Sommaire

- [Installation](#installation)
- [Marche à suivre](#marche-à-suivre)
- [FAQ](#faq)

### Installation

Cloner le projet :

```bash
git clone git@github.com:chartes/Nakalator.git
```

Méthode 1 (recommandé) :

```bash
make all 
```
puis tester l'installation :

```bash
python3 nakalator.py --help
```

Méthode 2 :

1. créer un environnement virtuel (par exemple avec virtualenv):
```bash
virtualenv -p python3.9 venv
```

2. activer l'environnement virtuel :
```bash
source venv/bin/activate
```

3. installer les dépendances :
```bash
pip3 install -r requirements.txt
```

4. tester l'installation :
```bash
python3 nakalator.py --help
```

### Marche à suivre

1. Éditer le fichier `credentials.yml` avec
la clé d'API Nakala correspondant a votre compte utilisateur Nakala. Si vous ne disposez pas
de clé d'API Nakala (Création d'un compte Human-id et demande d'accès à Nakala requis), vous pouvez utiliser une clé d'API de test sur https://test.nakala.fr/ (cette clé sera utilisable uniquement sur l'instance Nakala de test).

2. Déposer les images à envoyer dans un sous-dossier du dossier `data/`. Une donnée == un dossier == un lot d'images.
> [!TIP]
> Prévoyez un plan de nommage pour les images en amont de l'envoi, celui-ci déterminera l'ordre des images dans Nakala.

3. Créer et compléter le fichier `metadata_{nom_du_projet}.yml` (vous pouvez vous inspirer du fichier [`metadata_example.yml`](https://github.com/chartes/Nakalator/blob/master/metadatas/metadata_example.yml))
dans le dossier `metadatas/` qui rassemble les métadonées du lot d'image à envoyer.

> [!TIP]
> Pour plus d'informations sur les métadonnées Nakala : [documentation Nakala](https://documentation.huma-num.fr/nakala-guide-de-description/).

> [!TIP]
> Une fois la donnée créée il est toujours possible de modifier ou d'ajouter les métadonnées dans l'interface Nakala.

4. Enfin vous pouvez lancer le CLI avec la commande suivante et répondre aux instructions :

```bash
python3 nakalator.py -m [soft|hard|go]
```

Deux méthodes d'envoi sont disponibles :

- La méthode `soft` : cette méthode utilise un algorithme classique qui envoi les images une par une sur Nakala.
- La méthode `hard` : cette méthode utilise un algorithme qui envoi les images en parallèle (*multithreading*) sur Nakala.
- La méthode `go`  (expérimental)  : cette méthode utilise un algorithme qui envoi les images en parallèle (*go routines*) sur Nakala (les requêtes POST pour l'envoi des images est délégué à un script Go compilé).

Toutes ces méthodes utilisent des stratégies de *backoff exponentiel* et des *accumulateurs* pour gérer les éventuelles erreurs de connexion avec l'API Nakala. Cela doit permettre de nouvelles tentatives en cas d'échec jusqu'à l'envoi complet du lot d'images.

5. A la fin du processus, un fichier `{nom_du_projet}_mapping_ids_{date}.csv` sera généré dans le dossier `output/` contenant le *mapping* des images envoyés sur Nakala et des identifiants (DOI et sha1) (attention à bien archiver ce fichier qui sera utilisé pour la génération des manifestes IIIF).

6. A la fin du processus, vous pouvez passer dans l'interface Nakala pour vérifier que les images ont bien été envoyées : 
    - vous pouvez modifier manuellement les métadonnées des données
    - vous pouvez ajouter des fichiers supplémentaires (si nécéssaire)
    - vous pouvez utiliser un tri pour remettre les images dans l'ordre (Cf. [FAQ](#faq) pour plus d'informations)
    - vous pouvez passer en mode "publié" (au lieu de privé) pour que les données soient visibles par tous.
      
> [!WARNING]
> Le nombre de données en mode "privé" est limité sur Nakala, pensez à publier ces données au fur et à mesure.

> [!WARNING]
> Une fois la donnée "publié" dans Nakala, il n'est plus possible de la supprimer (contacter le support de Nakala).

### FAQ

- *Comment faire pour remettre les images dans l'ordre dans Nakala ?*

    > Vous pouvez vous rendre sur la page de la donnée créer dans Nakala : utiliser l'icône de tri et sauvegarder les modifications.
    
    ![capture-nakala](./documentation/capture_nakala_tri.png)
