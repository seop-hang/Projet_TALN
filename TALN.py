import xml.etree.ElementTree as ET
from fpdf import FPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from stop_words import get_stop_words
import matplotlib.pyplot as plt

class TALN:
    def __init__(self,corpuspath):
        """
        la fonction de l'initialisation
        :param corpuspath: le chemin de corpus
        """
        tree = ET.parse(corpuspath)
        # sauvgarder l'arbre de corpus
        self.corpustree=tree
        # sauvgarder la racine de l'arbre
        self.root=tree.getroot()
        self.resume=""

    def resume_selction(self,filtre,filtre_arg=None):
        """
        la fonction pour extraire tous les résumés ou les résumés filtrés
        :param filtre: choix entre "tous","annee" et "terme" pour indiquer si on fait le filtrage
                        "tous": sans filtrage
                        "annee" : filtrer les résumés selon une année
                        "terme": filtrer les résumés selon un mot clé
        :param filtre_arg: si on fait le filtrage, cet argument est utilisé comme un argument de filtrage
        :return: les résumés sélectionnés
        """
        # assurer que l'argument saisi est légal
        assert filtre.lower() in ["tous","annee","terme"]
        resume_filtre=""
        resumes=[]
        # on parcourt tous les articles dans le corpus, filtre les résumés selon le choix de l'utilisateur, et sauvegarde
        # les résumés dans la liste
        for i,article in enumerate(self.root):
            if filtre.lower()=="tous":
                # récupérer tous les résumés
                resume_fr = article.findall(".//*[@type='abstract']/{http://www.tei-c.org/ns/1.0}p")
                if resume_fr!=[]:
                    resume_fr=resume_fr[0]
                    resumes.append((i,resume_fr))
            elif filtre.lower()=="annee":
                # récupérer les résumés si la date correspond à ce que l'utilisateur saisit
                date = article.find(".//{http://www.tei-c.org/ns/1.0}date")
                if date.text == str(filtre_arg):
                    resume_fr = article.findall(".//*[@type='abstract']/{http://www.tei-c.org/ns/1.0}p")[0]
                    resumes.append((i,resume_fr))
            else:
                # récupérer les résumés si les mots clés de l'article comprend le terme saisi
                cles = article.findall(".//*[@type='keywords']/{http://www.tei-c.org/ns/1.0}p")
                keywords = set()
                for cle in cles:
                    if cle.text is not None and cle.text != "None":
                        cle_list = cle.text.replace("\n", "").split(",")
                        keywords.update(tuple([cle.strip().lower() for cle in cle_list]))
                if filtre_arg.lower() in keywords:
                    resume_fr = article.findall(".//*[@type='abstract']/{http://www.tei-c.org/ns/1.0}p")[0]
                    resumes.append((i,resume_fr))
        # on parcourt les résumés troués et les sauvegarde dans une chaine de caractère
        for resume in resumes:
            if resume[1].text is not None and resume[1].text != "None":
                resume_filtre += str(resume[0]) + " : \n"
                resume_filtre = resume_filtre + resume[1].text.replace("\n", "") + "\n"
        self.resume=resume_filtre
        return resume_filtre

    def resume_production(self,mode,mode_path=None):
        """
        la fonction pour sortir les résumés trouvés
        :param mode: choix entre "console","txt" et "pdf" pour indiquer la modalité à produire le résultat
                        "console": produire à la console
                        "txt" : produire dans un fichier texte
                        "pdf": produire dans un fichier pdf
        :param mode_path: si on produit le résultat dans un fichier, cet argument est utilisé pour indiquer le chemin
                        de fichier
        """
        # assurer que l'argument saisi est légal
        assert mode.lower() in ["console","txt","pdf"]
        # produire le résultat selon le choix
        if mode.lower()=="txt":
            # production dans un fichier texte
            try:
                file=open(mode_path,'w',encoding='utf8')
            except Exception as err:
                return "Impossible de créer ou ouvrir le fichier texte !"
            file.write(self.resume)
            file.close()
        elif mode.lower()=="pdf":
            # production dans un fichier pdf
            pdf = FPDF()
            pdf.add_page()
            # Configurer le style et la taille de la police
            pdf.set_font("Arial", size=12)
            # écrire les résumés dans le fichier pdf
            try:
                pdf.multi_cell(0, 10, self.resume.encode('latin-1', 'replace').decode('latin-1'))
            except Exception as err:
                return str(err)
            # sauvgarder le fichier pdf
            try:
                pdf.output(mode_path)
            except Exception as err:
                return "Impossible de créer ou ouvrir le fichier pdf !"
        else:
            # production à la console
            print(self.resume)

    def categorisation(self,num_clusters):
        """
        la fonction pour catégoriser les articles, cette catégorisation se base sur la similarité entre les résumés
        des articles
        :param num_clusters: le nombre de catégories
        :return: - vectors : la représentation des articles en vecteurs
                - labels : les catégories de chaque article
        """
        # créer un corpus (une liste) qui contient tous les résumés
        resumes=[]
        for i, article in enumerate(self.root):
            resume_fr = article.findall(".//*[@type='abstract']/{http://www.tei-c.org/ns/1.0}p")
            if resume_fr != []:
                resume_fr = resume_fr[0]
                if resume_fr.text is not None and resume_fr.text!="None":
                    resumes.append(resume_fr.text)

        # obtenir les stopwords français
        stopwords=get_stop_words('french')
        # utiliser TfidfVectorizer pour extraire les caractéristiques
        vectorizer = TfidfVectorizer(max_df=0.5, max_features=10000, min_df=2, stop_words=stopwords, use_idf=True)
        vectors = vectorizer.fit_transform(resumes)

        # faire le clustring acec kmeans
        kmeans = KMeans(n_clusters=num_clusters, init='k-means++', max_iter=100, n_init=1)
        kmeans.fit(vectors)

        # sortir les catégories de tous les articles
        labels = kmeans.labels_

        # écrire le résultat dans un fichier au format txt
        result_file="clustring_result.txt"
        with open(result_file, 'w',encoding='utf8') as file:
            for i, article in enumerate(resumes):
                file.write(f"article: {article}catégorie:\n{labels[i]}\n\n")
        return vectors,labels

    def vasualisation(self, tfidf_vectors, kmeans_labels):
        """
        la fonction pour la visualisation des catégorisation des articles
        :param tfidf_vectors: la représentation des articles en vecteurs
        :param kmeans_labels: les catégories de chaque article
        """
        tsne = TSNE(n_components=2)
        decomposition_data = tsne.fit_transform(tfidf_vectors)
        x = []
        y = []
        for i in decomposition_data:
            x.append(i[0])
            y.append(i[1])
        fig = plt.figure(figsize=(10, 10))
        ax = plt.axes()
        plt.scatter(x, y, c=kmeans_labels, marker="x")
        plt.xticks(())
        plt.yticks(())
        plt.show()

if __name__ == '__main__':
    # instanciqtion de la classe
    taln=TALN('./corpus_taln_v1.tei.xml')

    # utilisation de la méthode "resume_selction"
    resumes_tous=taln.resume_selction("tous")
    resumes_annee=taln.resume_selction("annee",2002)
    resumes_terme=taln.resume_selction("terme",'tal')

    # utilisation de la méthode "resume_production"
    taln.resume_production('console')
    taln.resume_production('txt', 'resume_output.txt')
    taln.resume_production('pdf','resume_output.pdf')

    # utilisation de la méthode "categorisation" et "vasualisation"
    vectors,labels=taln.categorisation(5)
    vectors=vectors.toarray()
    taln.vasualisation(vectors,labels)