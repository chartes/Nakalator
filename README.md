# Nakalator CLI

![python-versions](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C3.11-blue)

Nakalator est un outil en ligne de commande (CLI) conçu pour faciliter la création de dépôts et l'envoi de fichiers sur la plateforme [Nakala](https://nakala.fr/) <img src="./assets/nakala.png" width="15px">

Nakalator permet de :
- Créer un dépôt sur Nakala avec des métadonnées associées en utilisant un fichier YAML.
- Envoyer des fichiers (par exemple, des images) sur Nakala associés à une donnée spécifique.
- Créer une collection de données ou rattacher des données à une collection existante sur Nakala.

Il peut être considéré comme une alternative à l'outil [Mynkl](https://mynkl.huma-num.fr/).

Les avantages de Nakalator sont les suivants :

- **Retour utilisateur** : Nakalator permet de suivre en temps réel le nombre de fichiers en cours d'envoi sur Nakala.
- **Performances** : En fonction de la machine utilisée et de la quantité de fichiers, Nakalator réduit le temps d'envoi des fichiers sur Nakala grâce à une méthode d'envoi **multi-threads** (goroutines).
- **Intégrité des données** : Génération d'un fichier de *mapping* des fichiers envoyés sur Nakala, avec les identifiants DOI et SHA-1. Des vérifications sont effectuées après l'envoi des fichiers.

----

## Sommaire

- [Installation](#installation)
- [Marche à suivre](#marche-à-suivre)
- [FAQ](#faq)

### Installation

1. Clonez le projet :

```bash
git clone git@github.com:chartes/Nakalator.git
cd Nakalator/
```

2. (Optionnel) Créez un environnement virtuel avec `virtualenv`, `pyenv`, etc. Par exemple, avec `virtualenv` :

```bash
virtualenv -p python3.9 venv
source venv/bin/activate
```

3. Installez le CLI :

```bash
pip install -e .
```

4. Testez l'installation :

```bash
nakalator --help
```

#### Pour le développement (uniquement)

1. Clonez le projet :

```bash
git clone git@github.com:chartes/Nakalator.git
cd Nakalator/
```

2. Utilisez `make` pour installer le CLI (attention, cela utilise `virtualenv`) :

```bash
make all
```

3. Pour lancer l'outil :

```bash
python3 nakalator.py --help
```

- Pour compiler l'ensemble du projet (sources Go, build, dist, etc.) avant la distribution via Pypi depuis `Naklator/` :

```bash
make build_pkg VERSION_PKG=0.0.1-beta # exemple de version à spécifier 
```

- En cas de modification des sources Go, vous pouvez recompiler le binaire depuis `Naklator/` :

```bash
make build_go
```

Dans ce dernier cas, l'installation préalable du langage Go est nécessaire.

### Marche à suivre

1. Une fois l'installation effectuée, et pour la première utilisation de l'outil, commencez par créer votre environnement de travail (nommé `nakalator_workspace`) :

```bash
nakalator init
```
Cela créera un dossier `nakalator_workspace/` dans votre répertoire courant. Ce dossier contiendra les fichiers de configuration temporaires nécessaires pour l'envoi des données sur Nakala (`metadatas/`), les fichiers à envoyer (`data/`), ainsi que les fichiers de mapping des données envoyées (`output/`). Notez également la présence d'un fichier `credentials.yml` pour renseigner les informations de connexion à Nakala (clés API).
Toutes les commandes Nakalator doivent être exécutées dans le répertoire `nakalator_workspace/`.

2. L'organisation des fichiers de métadonnées YAML et des fichiers à envoyer est cruciale.
Plusieurs cas d'usage sont possibles, les plus courants sont :

- **Création d'une donnée sur Nakala (rattachée ou non à une collection existante ou nouvelle) avec des fichiers associés (par exemple, des images)** :
  1. Déposez votre fichier YAML (préalablement rempli) dans le dossier `metadatas/` (par exemple `metadatas/mon_projet.yml`) ;
  2. Déposez vos images dans un dossier spécifique dans `data/` (par exemple `data/mon_projet/image1.jpg`, `data/mon_projet/image2.jpg`, etc.).

- **Création de plusieurs données sur Nakala (rattachées ou non à une collection existante ou nouvelle) avec des fichiers associés (par exemple, des images) pour chacune d'elles** :
  1. Déposez vos fichiers YAML (préalablement remplis) dans le dossier `metadatas/` (par exemple `metadatas/mon_projet/mon_projet1_1.yml`, `metadatas/mon_projet/mon_projet1_2.yml`) ;
  2. Déposez vos images dans un dossier spécifique dans `data/` (par exemple `data/mon_projet1_1/image1.jpg`, `data/mon_projet1_1/image2.jpg`, `data/mon_projet1_2/image1.jpg`, `data/mon_projet1_2/image2.jpg`, etc.).

> [!TIP]
> Pour remplir le fichier YAML, vous pouvez vous inspirer du fichier `metadata_example.yml` présent dans le dossier `nakalator_workspace/` lors de l'initialisation de l'environnement de travail. Vous pouvez également consulter le dossier `examples/` qui contient des exemples de fichiers de métadonnées inspirés d'autres projets.

> [!TIP]
> Prévoyez un plan de nommage rigoureux pour les images avant l'envoi, car cela déterminera l'ordre des images dans Nakala.

> [!TIP]
> Si vous avez plusieurs données à créer, vous pouvez utiliser les suffixes spéciaux `_PREV` et `_NEXT`. La donnée avec le suffixe `_PREV` sera automatiquement placée en première position et celle avec le suffixe `_NEXT` en dernière position. Cela peut être utile pour les pages liminaires et postliminaires d'un document, par exemple.

> [!TIP]
> Pour plus d'informations sur les métadonnées Nakala, consultez la [documentation Nakala](https://documentation.huma-num.fr/nakala-guide-de-description/).

3. Une fois l'étape 2 terminée, vous pouvez lancer l'envoi des données sur Nakala depuis le répertoire `nakalator_workspace/` :

```bash
nakalator main
```

Suivez les instructions et répondez aux questions posées par le CLI.

> [!TIP]
> Une fois la donnée créée, il est toujours possible de modifier ou d'ajouter des métadonnées dans l'interface Nakala.

4. À la fin du processus, un ou plusieurs fichiers de mapping seront générés dans le dossier `output/` de votre `nakalator_workspace/`. Le nommage est le suivant :

   - Donnée rattachée à une collection : `data_{ordre}_{doi_de_la_collection}_{doi_de_la_donnee}.csv`
   - Donnée non rattachée à une collection : `data_{ordre}_{doi_de_la_donnee}.csv`

Ce fichier, à bien conserver, contient l'ensemble des fichiers envoyés sur Nakala avec les identifiants DOI et SHA-1 associés (ce qui peut être utile pour la génération de manifestes IIIF, par exemple).

5. Vous pouvez vérifier dans l'interface Nakala que les données ont bien été envoyées :

- Modifier manuellement les métadonnées des données.
- Ajouter des fichiers supplémentaires si nécessaire.
- Utiliser un tri pour remettre les images dans l'ordre (cf. [FAQ](#faq) pour plus d'informations).
- Passer en mode "publié" (au lieu de "privé") pour que les données soient visibles par tous.

> [!WARNING]
> Le nombre de données en mode "privé" est limité sur Nakala, pensez à publier ces données au fur et à mesure.

> [!WARNING]
> Une fois la donnée "publiée" dans Nakala, il n'est plus possible de la supprimer (contactez le support de Nakala).

### FAQ

- **Comment remettre les images dans l'ordre sur Nakala ?**

    > Vous pouvez vous rendre sur la page de la donnée créée dans Nakala, utiliser l'icône de tri, puis sauvegarder les modifications.
    
    ![capture-nakala](./assets/capture_nakala_tri.png)