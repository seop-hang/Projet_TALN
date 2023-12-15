# TALN Script

## Introduction

Le script TALN (Traitement Automatique du Langage Naturel) est conçu pour extraire des résumés à partir d'un corpus 
au format TEI XML. Il propose plusieurs fonctionnalités, y compris la lecture et le filtrage du corpus en utilisant
xml.etree.ElementTree et le clustring des résumés en utilisant scikit-learn.

## Fonctionnalités

1. **`resume_selction`**: Extraire des résumés en fonction de différents filtres.
   - `tous`: Extraire tous les résumés.
   - `annee`: Extraire les résumés d'une année spécifique.
   - `terme`: Extraire les résumés contenant un mot-clé spécifique.

3. **`resume_production`**: Produire les résumés sous différentes formes.
   - `console`: Afficher les résumés dans la console.
   - `txt`: Sauvegarder les résumés dans un fichier texte.
   - `pdf`: Générer un fichier PDF contenant les résumés.

4. **`categorisation`**: Catégoriser les articles à l'aide de l'algorithme de clustering KMeans.

## Utilisation

1. **Installer les dépendances**:
   ```bash
   pip install xmltodict fpdf scikit-learn stop-words

2. **Exécuter le script**:
   ```bash
   python TALN.py
   
3. **Exemples d'utilisation**
- Extraire tous les résumés:
   ```bash
   resumes_tous = taln.resume_selction("tous")
- Extraire les résumés d'une année spécifique
   ```bash
   resumes_annee = taln.resume_selction("annee", 2002)
- Extraire les résumés contenant un mot-clé spécifique
   ```bash
   resumes_terme = taln.resume_selction("terme", 'tal')
- Afficher les résumés dans la console
   ```bash
   taln.resume_production('console')
- Sauvegarder les résumés dans un fichier texte
   ```bash
   taln.resume_production('txt', 'resume_output.txt')
- Générer un fichier PDF contenant les résumés
   ```bash
   taln.resume_production('pdf', 'resume_output.pdf')
- Catégoriser les articles et visualiser le résultat de catégorisation
   ```bash
    vectors,labels=taln.categorisation(5)
    vectors=vectors.toarray()
    taln.vasualisation(vectors,labels)

## Fichiers
1. **TALN.py**:
- le fichier de script proposant les fonctions de création et production du livret de résumés, ainsi que le clustring des résumés

2. **corpus_taln_v1.tei.xml**:
- le corpus TALN

3. **resume_output.txt**:
- l'exemple de production du livret de résumés dans un fichier texte

4. **resume_output.pdf**:
- l'exemple de production du livret de résumés dans un fichier pdf

5. **clustring_result.txt**:
- l'exemple de conservation du résultat de clustring des résumés dans un fichier texte