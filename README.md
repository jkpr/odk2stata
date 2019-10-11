Check out the docs hosted over at [Amazon S3](http://odk2stata-docs.s3-website-us-west-2.amazonaws.com/)

# Installation

To install `odk2stata` for the first time, run:

```
python3 -m pip install odk2stata
```

### Upgrade

If you already have `odk2stata` installed, then run:

```
python3 -m pip install odk2stata --upgrade
```

# Generate a Stata do file from an XlsForm

The do file does various useful things, including:

- Import the dataset with all string variables
- Drop columns, notes by default
- Rename columns
- Destring numeric types
- Encode `select_one` variables with the name or the label
- Split `select_multiple` variables
- Label the column variables, using the label by default

---

# Installation

Pour installer `odk2stata` pour la première fois, lancez :

```
python3 -m pip install odk2stata
```

### Ameliorer

Si vous avez déjà installé `odk2stata`, lancez :

```
python3 -m pip install odk2stata --upgrade
```

# Gênerez un fichier Stata do  à partir d’un XlsForm

Le fichier do fait diverses choses utiles, y compris :

- Importer l’ensemble de données avec tous les strings de variables
- Déposez les colonnes ainsi que aussi les notes par défaut
- Rebaptiser les colonnes
- (Destring) Conversion de variables numériques en variables en chaîne
- Encoder les variables avec le nom ou le label `select_one`
- Fractionner les variables `select multiple
- Labelliser les variables de colonne, en utilisant le label par défaut
