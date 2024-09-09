#!/usr/bin/env python3
# -- coding: utf-8 --

"""This file contains the user assets for the project that convert to yaml
"""

credentials_to_yaml = "API_NAKALA_KEY_PROD: \"indiquer votre clé ici\" # Remplir avec la clé API " \
                      "si vous utilisez l'instance Nakala en production\n" \
                      "API_NAKALA_KEY_TEST: \"indiquer votre clé ici\" # Remplir avec la clé API " \
                      "si vous utilisez l'instance Nakala en test"

metadata_to_yaml = """# ***************************************************************************
# FICHIER D'EXEMPLE POUR LA CRÉATION DE MÉTADONNÉES                         *
# NE PAS SUPPRIMER CE FICHIER                                               *
# UTILISER CE FICHIER COMME MODÈLE POUR CRÉER DE NOUVELLES MÉTADONNÉES      *
# ***************************************************************************

name: "BELLELAY" # Nom du projet nakalator (de préférence le préfixe utilisé pour les images)

################################################################################################
# ZONE DONNÉE
################################################################################################

data:
  path: "/Users/user/Documents/dev/nakalator_workspace/data/mon_projet_1/mon_projet_1_1/" # Chemin absolu (!) vers le répertoire des données dans nakalator_workspace/data/mon_dossier_contenant_les_images/ par exemple le dossier contenant l'image ou les images 
  type: "tif" # Format des images (jpeg, tif, png, etc.)
  status: "pending" # "pending" ou "published". Il est conseillé de laisser "pending" par défaut et de changer le status dans Nakala une fois le dépôt validé manuellement.

################################################################################################
# ZONE COLLECTION
################################################################################################

collectionIds: "" # Utiliser le DOI de la collection présent dans Nakala si les images sont déposées dans une collection existante, sinon laisser vide.
collectionTitle: "Le nom de ma collection à créer" # A remplir si je souhaite créer une nouvelle collection au moment du dépôt de ma ou de mes données, sinon laisser vide.
collectionDescription: "La description de ma collection à créer" # A remplir si je souhaite créer une nouvelle collection au moment du dépôt de ma ou de mes données, sinon laisser vide.
collectionStatus: "private" # "private" ou "public". Il est conseillé de laisser "private" par défaut et de changer le status dans Nakala une fois le versement de la ou des données réalisé.

################################################################################################
# ZONE MÉTADONNÉES DE LA DONNÉE
################################################################################################

metadata:
  # ===========================================================================
  # * Métadonnées obligatoires pour le dépôt dans Nakala *
  # à compléter manuellement sinon elles seront générés automatiquement avec des valeurs par défaut.
  # ===========================================================================
  
  http://nakala.fr/terms#title: # Le titre de la donnée qui s'affiche dans la page de présentation de la donnée sur Nakala
    value : "Images du graduel de Bellelay" # a modifier
    lang : "fr"
    typeUri: "http://www.w3.org/2001/XMLSchema#string"

  http://purl.org/dc/terms/description: # Description de la donnée qui s'affiche dans la page de présentation de la donnée sur Nakala
    value: "Le graduel de Bellelay est l'un des premiers livres liturgiques notés de l'ordre des Prémontrés. Il contient tout le répertoire des messes et des offices pour le cycle liturgique de l'année, plus quelques ajouts marginaux (compositions musicales, donation)." # a modifier
    lang: "fr"
    typeUri: "http://www.w3.org/2001/XMLSchema#string"


  http://nakala.fr/terms#creator: # Créateur de la donnée (vous pouvez entièrement commenter ce champ, par défaut la métadonnée sera alors "anonyme")
    value:
      givenname: "Toto"
      surname: "Tati"

  http://nakala.fr/terms#created: # Date de création de la donnée (vous pouvez entièrement commenter ce champ, par défaut la date du jour sera alors indiqué)
    value: "2024-09-02"
    typeUri: "http://www.w3.org/2001/XMLSchema#string"


  http://nakala.fr/terms#license: # Licence de la donnée dans Nakala (si vous commenter entièrement, la licence 'CC-BY-4.0' sera appliqué par défaut). Pour les codes licences acceptés par Nakala voir : https://api.nakala.fr/vocabularies/licenses 
    value: "CC-BY-4.0"
    typeUri: "http://www.w3.org/2001/XMLSchema#string"

  http://nakala.fr/terms#type: # Type de dépôt Nakala, par défaut "c_c513" (image). Pour les formats acceptés par Nakala voir : https://api.nakala.fr/vocabularies/licenses
    value: "http://purl.org/coar/resource_type/c_c513"
    typeUri: "http://www.w3.org/2001/XMLSchema#anyURI"

  http://purl.org/dc/terms/publisher: # Publication, si commenté "École nationale des chartes - PSL" par défaut
    value: "École nationale des chartes - PSL"
    lang: "fr"
    typeUri: "http://www.w3.org/2001/XMLSchema#string"

  # ===========================================================================
  # * Métadonnées facultatives pour le dépôt dans Nakala *
  # Ajouter d'autres métadonnées qualifiées si nécessaire avec d'autres schémas (https://documentation.huma-num.fr/nakala-guide-de-description/)
  # ===========================================================================

  http://purl.org/dc/terms/title:
    value: "Un autre titre"
    typeUri: "http://www.w3.org/2001/XMLSchema#string"
  
  http://purl.org/dc/terms/extent:
    value: "0-8"
    lang: "fr"
    typeUri: "http://www.w3.org/2001/XMLSchema#string"
  
  http://purl.org/dc/terms/date:
    value: "1988"
    lang: "fr"
    typeUri: "http://www.w3.org/2001/XMLSchema#string"

  http://purl.org/dc/terms/bibliographicCitation:
    value : "auteur, « titre », in ouvrage etc."
    lang: "fr"
    typeUri: "http://www.w3.org/2001/XMLSchema#string"


  # http://purl.org/dc/terms/creator:
  # http://purl.org/dc/terms/contributor:
  # http://purl.org/dc/terms/language:
  # http://purl.org/dc/terms/relation:
  # http://purl.org/dc/terms/rightsHolder:
  # http://purl.org/dc/terms/spatial:
  # http://purl.org/dc/terms/available:
  # http://purl.org/dc/terms/modified:
  # http://purl.org/dc/terms/rights:
  # http://purl.org/dc/terms/isVersionOf:
  # http://purl.org/dc/terms/format:
  # http://purl.org/dc/terms/abstract:
  # http://purl.org/dc/terms/source:
  # http://purl.org/dc/terms/subject:
  # http://purl.org/dc/terms/medium:
  # ...
"""

workspace_info_init = lambda base_dir_create: f"""
    📁 {base_dir_create}
        ├── 📁 data/ : This directory contains the data to be sent to Nakala (images, xml, pdf, audio records etc.)
        ├── 📁 metadatas/ : This directory contains the metadata files in YAML format
        ├           ├── 📄 metadata_example.yml : Example file for creating metadata
        ├── 📁 output/ : This directory contains the output files (reports to check output of the process)
        ├── 📄 credentials.yml : This file contains the Nakala API key for test and production

        Process: 
        1. Go to workspace directory with 'cd ./nakalator_workspace/'
        2. If necessary, add Nakala API key in credentials.test.yml or credentials.prod.yml
        3. Add data to the data/ directory
        4. Create metadata files in the metadatas/ directory (you can use metadata_example.yml as a template)
        5. Send data to Nakala with command 'nakalator main'
    """
