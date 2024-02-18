
"""

"C:/Users/username/AppData/Local/nomic.ai/GPT4All/ggml-gpt4all-l13b-snoozy.bin"

Prompt-Templates:
 ### Response:

gpt4all.GPT4All.download_model('ggml-gpt4all-l13b-snoozy.bin','.')

Models: https://raw.githubusercontent.com/nomic-ai/gpt4all/main/gpt4all-chat/metadata/models2.json

{
  "type": "chat",
  "prompt": ""
}
 
"""
import sys
import os.path
import random

from nwebclient import runner
from nwebclient import util

# see more at https://pi.bsnx.net/jupyter/notebooks/notebooks/Datenanalyse/Daten%20Generierung.ipynb

de_firstname_male = [
    "Peter", "Wolfgang", "Michael", "Werner", "Klaus", "Thomas", "Manfred", "Helmut",
    "Jürgen", "Heinz", "Gerhard", "Andreas", "Hans", "Josef", "Günter", "Dieter",
    "Horst", "Walter", "Frank", "Bernd", "Karl", "Herbert", "Franz", "Martin", "Uwe",
    "Georg", "Heinrich", "Stefan", "Christian", "Karl-Heinz", "Rudolf", "Kurt",
    "Hermann", "Johann", "Wilhelm", "Siegfried", "Rolf", "Joachim", "Alfred", "Rainer",
    "Jörg", "Ralf", "Erich", "Norbert", "Bernhard", "Willi", "Alexander", "Ulrich",
    "Markus", "Matthias", "Harald", "Paul", "Roland", "Ernst", "Reinhard", "Günther",
    "Gerd", "Fritz", "Otto", "Friedrich", "Erwin", "Lothar", "Robert", "Dirk",
    "Johannes", "Volker", "Wilfried", "Richard", "Anton", "Jens", "Hans-Jürgen",
    "Hubert", "Udo", "Holger", "Albert", "Ludwig", "Dietmar", "Hartmut", "Reinhold",
    "Hans-Joachim", "Adolf", "Detlef", "Oliver", "Christoph", "Stephan", "Axel",
    "Reiner", "Alois", "Eberhard", "Waldemar", "Heiko", "Daniel", "Torsten", "Sven",
    "Bruno", "Olaf", "Mario", "Konrad", "Steffen", "Ingo",
]

de_firstname_female = [
    "Maria", "Ursula", "Monika", "Petra", "Elisabeth", "Sabine", "Renate", "Helga","Karin",
    "Brigitte", "Ingrid", "Erika", "Andrea", "Gisela", "Claudia", "Susanne", "Gabriele",
    "Christa", "Christine", "Hildegard", "Anna", "Birgit", "Barbara", "Gertrud",
    "Heike", "Marianne", "Elke", "Martina", "Angelika", "Irmgard", "Inge", "Ute","Elfriede",
    "Doris", "Marion", "Ruth", "Ulrike", "Hannelore", "Jutta", "Gerda", "Kerstin", "Ilse",
    "Anneliese", "Margarete", "Ingeborg", "Anja", "Edith", "Sandra", "Waltraud", "Beate",
    "Rita", "Katharina", "Christel", "Nicole", "Regina", "Eva", "Rosemarie", "Erna",
    "Manuela", "Sonja", "Johanna", "Irene", "Silke", "Gudrun", "Christiane", "Cornelia",
    "Tanja", "Anita", "Bettina", "Silvia", "Daniela", "Sigrid", "Simone", "Stefanie",
    "Annette", "Bärbel", "Michaela", "Angela", "Dagmar", "Heidi", "Annemarie", "Helene",
    "Anke", "Margot", "Sylvia", "Christina", "Katrin", "Melanie", "Hedwig", "Roswitha",
    "Martha", "Alexandra", "Else", "Iris", "Katja", "Charlotte", "Lieselotte", "Hilde",
    "Astrid", "Anni"
]

# https://de.wiktionary.org/wiki/Verzeichnis:Deutsch/Namen/die_h%C3%A4ufigsten_Nachnamen_Deutschlands
de_lastname = [
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker",
    "Schulz", "Hoffmann", "Schäfer", "Bauer", "Koch", "Richter", "Klein", "Wolf", "Schröder",
    "Neumann", "Schwarz", "Braun", "Hofmann", "Zimmermann", "Schmitt", "Hartmann", "Krüger",
    "Schmid", "Werner", "Lange", "Schmitz", "Meier", "Krause", "Maier", "Lehmann", "Huber",
    "Mayer", "Herrmann", "Köhler", "Walter", "König", "Schulze", "Fuchs", "Kaiser", "Lang",
    "Weiß", "Peters", "Scholz", "Jung", "Möller", "Hahn", "Keller", "Vogel", "Schubert",
    "Roth", "Frank", "Friedrich", "Beck", "Günther", "Berger", "Winkler", "Lorenz", "Baumann",
    "Schuster", "Kraus", "Böhm", "Simon", "Franke", "Albrecht", "Winter", "Ludwig", "Martin",
    "Krämer", "Schumacher", "Vogt", "Jäger", "Stein", "Otto", "Groß", "Sommer", "Haas",
    "Graf", "Heinrich", "Seidel", "Schreiber", "Ziegler", "Brandt", "Kuhn", "Schulte",
    "Dietrich", "Kühn", "Engel", "Pohl", "Horn", "Sauer", "Arnold", "Thomas", "Bergmann",
    "Busch", "Pfeiffer", "Voigt", "Götz", "Seifert", "Lindner", "Ernst", "Hübner", "Kramer",
    "Franz", "Beyer", "Wolff", "Peter", "Jansen", "Kern", "Barth", "Wenzel", "Hermann",
    "Ott", "Paul", "Riedel", "Wilhelm", "Hansen", "Nagel", "Grimm", "Lenz", "Ritter",
    "Bock", "Langer", "Kaufmann", "Mohr", "Förster", "Zimmer", "Haase", "Lutz", "Kruse",
    "Jahn", "Schumann", "Fiedler", "Thiel", "Hoppe", "Kraft", "Michel", "Marx", "Fritz",
    "Arndt", "Eckert", "Schütz", "Walther", "Petersen", "Berg", "Schindler", "Kunz",
    "Reuter", "Sander", "Schilling", "Reinhardt", "Frey", "Ebert", "Böttcher", "Thiele",
    "Gruber", "Schramm", "Hein", "Bayer", "Fröhlich", "Voß", "Herzog", "Hesse", "Maurer",
    "Rudolph", "Nowak", "Geiger", "Beckmann", "Kunze", "Seitz", "Stephan", "Büttner",
    "Bender", "Gärtner", "Bachmann", "Behrens", "Scherer", "Adam", "Stahl", "Steiner",
    "Kurz", "Dietz", "Brunner", "Witt", "Moser", "Fink", "Ullrich", "Kirchner",
    "Löffler", "Heinz", "Schultz", "Ulrich", "Reichert", "Schwab", "Breuer", "Gerlach",
    "Brinkmann", "Göbel",
]

en_firstname_male = [
    "Liam", "Noah", "Oliver", "Elijah", "William", "James", "Benjamin", "Lucas",
    "Henry", "Alexander", "Mason", "Michael", "Ethan", "Daniel", "Jacob", "Logan",
    "Jackson", "Levi", "Sebastian", "Mateo", "Jack", "Owen", "Theodore",
    "Aiden", "Samuel", "Joseph", "John", "David", "Wyatt", "Matthew"]

en_firstname_female = [
    "Olivia", "Emma", "Ava", "Charlotte", "Sophia", "Amelia", "Isabella", "Mia",
    "Evelyn", "Harper", "Camila", "Gianna", "Abigail", "Luna", "Ella", "Elizabeth",
    "Sofia", "Emily", "Avery", "Mila", "Scarlett", "Eleanor", "Madison", "Layla",
    "Penelope", "Aria", "Chloe", "Grace", "Ellie", "Nora"]

en_lastname = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson",
    "Anderson", "Taylor", "Garcia", "Thomas", "Moore", "Martin", "Rodriguez", "Lee",
    "White", "Thompson", "Jackson", "Martinez", "Harris", "Clark", "Hernandez",
    "Lopez", "Lewis", "Walker", "Robinson", "Allen", "Gonzalez", "Young", "Hall",
    "Wright", "King", "Adams", "Nelson", "Scott", "Hill", "Baker", "Green", "Perez",
    "Campbell", "Carter", "Mitchell", "Roberts", "Sanchez", "Phillips", "Evans",
    "Turner", "Parker", "Edwards", "Collins", "Ramirez", "Stewart", "Morris",
    "Nguyen", "Murphy", "Cook", "Rogers", "Torres", "Peterson"]

# https://de.wiktionary.org/wiki/Verzeichnis:Deutsch/Berufe
de_job = [
    "Baggerfahrer", "Bahnangestellte", "Bandagist", "Bandreißer", "Bankkaufmann", "Barbier",
    "Bassist", "Bauarbeiter",  "Bauer",  "Baugeräteführer",  "Baustoffprüfer", "Bautechniker",
    "Bauwerksmechaniker", "Bauzeichner", "Fachkraft für Hygieneüberwachung",
    "Fachkraft für Kreislauf- und Abfallwirtschaft", "Fachkraft für Kurier-, Express- und Postdienstleistungen",
    "Fachkraft für Lagerlogistik", "Fachkraft für Lebensmitteltechnik", "Fachkraft für Lederverarbeitung",
    "Fachkraft für Möbel-, Küchen- und Umzugsservice", "Fachkraft für Pflegeassistenz",
    "Fachkraft für Rohr-, Kanal- und Industrieservice", "Fachkraft für Schutz und Sicherheit",
    "Fachkraft für Straßen- und Verkehrstechnik", "Kartograph", "Kinderarzt", "Koch"
]

de_orte = [{'Stadt': 'Berlin', 'PLZ': 10178}, {'Stadt': 'Hamburg', 'PLZ': 20038}, {'Stadt': 'München', 'PLZ': 80331},
 {'Stadt': 'Köln', 'PLZ': 50667}, {'Stadt': 'Frankfurt am Main', 'PLZ': 60311}, {'Stadt': 'Stuttgart', 'PLZ': 70173},
 {'Stadt': 'Düsseldorf', 'PLZ': 40213}, {'Stadt': 'Dortmund', 'PLZ': 44135}, {'Stadt': 'Essen', 'PLZ': 45127},
 {'Stadt': 'Bremen', 'PLZ': 28195}, {'Stadt': 'Hannover', 'PLZ': 30159}, {'Stadt': 'Leipzig', 'PLZ': 4109},
 {'Stadt': 'Dresden', 'PLZ': 1067}, {'Stadt': 'Nürnberg', 'PLZ': 90403}, {'Stadt': 'Duisburg', 'PLZ': 47051},
 {'Stadt': 'Bochum', 'PLZ': 44787}, {'Stadt': 'Wuppertal', 'PLZ': 42275}, {'Stadt': 'Bielefeld', 'PLZ': 33602},
 {'Stadt': 'Bonn', 'PLZ': 53111}, {'Stadt': 'Mannheim', 'PLZ': 68159}, {'Stadt': 'Karlsruhe', 'PLZ': 76133},
 {'Stadt': 'Wiesbaden', 'PLZ': 65183}, {'Stadt': 'Münster', 'PLZ': 48143}, {'Stadt': 'Augsburg', 'PLZ': 86150},
 {'Stadt': 'Gelsenkirchen', 'PLZ': 45879}, {'Stadt': 'Aachen', 'PLZ': 52062},
 {'Stadt': 'Mönchengladbach', 'PLZ': 41061}, {'Stadt': 'Braunschweig', 'PLZ': 38100},
 {'Stadt': 'Chemnitz', 'PLZ': 9111}, {'Stadt': 'Kiel', 'PLZ': 24103}, {'Stadt': 'Krefeld', 'PLZ': 47803},
 {'Stadt': 'Halle-Saale', 'PLZ': 6108}, {'Stadt': 'Magdeburg', 'PLZ': 39104},
 {'Stadt': 'Freiburg im Breisgau', 'PLZ': 79098}, {'Stadt': 'Oberhausen', 'PLZ': 46045},
 {'Stadt': 'Lübeck', 'PLZ': 23539}, {'Stadt': 'Erfurt', 'PLZ': 99084}, {'Stadt': 'Rostock', 'PLZ': 18055},
 {'Stadt': 'Mainz', 'PLZ': 55116}, {'Stadt': 'Kassel', 'PLZ': 34117}, {'Stadt': 'Hagen', 'PLZ': 58095},
 {'Stadt': 'Hamm', 'PLZ': 59065}, {'Stadt': 'Saarbrücken', 'PLZ': 66111},
 {'Stadt': 'Mülheim an der Ruhr', 'PLZ': 45468}, {'Stadt': 'Herne', 'PLZ': 44623}, {'Stadt': 'Osnabrück', 'PLZ': 49074},
 {'Stadt': 'Ludwigshafen am Rhein', 'PLZ': 67059}, {'Stadt': 'Oldenburg', 'PLZ': 26122},
 {'Stadt': 'Solingen', 'PLZ': 42651}, {'Stadt': 'Leverkusen', 'PLZ': 51373}, {'Stadt': 'Potsdam', 'PLZ': 14461},
 {'Stadt': 'Neuss', 'PLZ': 41460}, {'Stadt': 'Heidelberg', 'PLZ': 69117}, {'Stadt': 'Paderborn', 'PLZ': 33098},
 {'Stadt': 'Darmstadt', 'PLZ': 64283}, {'Stadt': 'Regensburg', 'PLZ': 93047}, {'Stadt': 'Würzburg', 'PLZ': 97070},
 {'Stadt': 'Ingolstadt', 'PLZ': 85049}, {'Stadt': 'Heilbronn', 'PLZ': 74072},
 {'Stadt': 'Ulm', 'PLZ': 89073}, {'Stadt': 'Göttingen', 'PLZ': 37083}, {'Stadt': 'Wolfsburg', 'PLZ': 38440},
 {'Stadt': 'Pforzheim', 'PLZ': 75175}, {'Stadt': 'Recklinghausen', 'PLZ': 45657},
 {'Stadt': 'Offenbach am Main', 'PLZ': 63065}, {'Stadt': 'Bottrop', 'PLZ': 46236}, {'Stadt': 'Fürth', 'PLZ': 90762},
 {'Stadt': 'Bremerhaven', 'PLZ': 27576}, {'Stadt': 'Reutlingen', 'PLZ': 72764},
 {'Stadt': 'Remscheid', 'PLZ': 42853}, {'Stadt': 'Koblenz', 'PLZ': 56068}, {'Stadt': 'Moers', 'PLZ': 47441},
 {'Stadt': 'Bergisch Gladbach', 'PLZ': 51465}, {'Stadt': 'Erlangen', 'PLZ': 91052}, {'Stadt': 'Trier', 'PLZ': 54290},
 {'Stadt': 'Jena', 'PLZ': 7743}, {'Stadt': 'Siegen', 'PLZ': 57072}, {'Stadt': 'Salzgitter', 'PLZ': 38226},
 {'Stadt': 'Hildesheim', 'PLZ': 31134}, {'Stadt': 'Cottbus', 'PLZ': 3046}, {'Stadt': 'Gera', 'PLZ': 7545},
 {'Stadt': 'Kaiserslautern', 'PLZ': 67657}, {'Stadt': 'Witten', 'PLZ': 58452}, {'Stadt': 'Gütersloh', 'PLZ': 33330},
 {'Stadt': 'Iserlohn', 'PLZ': 58636}, {'Stadt': 'Schwerin', 'PLZ': 19053}, {'Stadt': 'Zwickau', 'PLZ': 8056},
 {'Stadt': 'Düren', 'PLZ': 52349}, {'Stadt': 'Esslingen am Neckar', 'PLZ': 73728}, {'Stadt': 'Ratingen', 'PLZ': 40878},
 {'Stadt': 'Flensburg', 'PLZ': 24937}, {'Stadt': 'Hanau', 'PLZ': 63450}, {'Stadt': 'Marl', 'PLZ': 45768},
 {'Stadt': 'Tübingen', 'PLZ': 72070}, {'Stadt': 'Lünen', 'PLZ': 44532}, {'Stadt': 'Dessau-Roßlau', 'PLZ': 6844},
 {'Stadt': 'Ludwigsburg', 'PLZ': 71638}, {'Stadt': 'Velbert', 'PLZ': 42551}, {'Stadt': 'Konstanz', 'PLZ': 78462},
 {'Stadt': 'Minden', 'PLZ': 32423}, {'Stadt': 'Worms', 'PLZ': 67547}, {'Stadt': 'Wilhelmshaven', 'PLZ': 26382},
 {'Stadt': 'Villingen-Schwenningen', 'PLZ': 78050}, {'Stadt': 'Marburg', 'PLZ': 35037}, {'Stadt': 'Dorsten', 'PLZ': 46284},
 {'Stadt': 'Neumünster', 'PLZ': 24534}, {'Stadt': 'Rheine', 'PLZ': 48431}, {'Stadt': 'Gießen', 'PLZ': 35390},
 {'Stadt': 'Lüdenscheid', 'PLZ': 58507}, {'Stadt': 'Castrop-Rauxel', 'PLZ': 44575}, {'Stadt': 'Gladbeck', 'PLZ': 45964},
 {'Stadt': 'Viersen', 'PLZ': 41747}, {'Stadt': 'Troisdorf', 'PLZ': 53840}, {'Stadt': 'Arnsberg', 'PLZ': 59759},
 {'Stadt': 'Delmenhorst', 'PLZ': 27749}, {'Stadt': 'Bocholt', 'PLZ': 46395}, {'Stadt': 'Detmold', 'PLZ': 32756},
 {'Stadt': 'Lüneburg', 'PLZ': 21335}, {'Stadt': 'Bayreuth', 'PLZ': 95444},
 {'Stadt': 'Brandenburg an der Havel', 'PLZ': 14770}, {'Stadt': 'Norderstedt', 'PLZ': 22846}]

de_street_names = [
    "Hauptstraße", "Gartenstraße", "Bahnhofstraße", "Dorfstraße", "Bergstraße",
    "Birkenweg",  "Lindenstraße", "Kirchstraße", "Waldstraße", "Ringstraße",
    "Schillerstraße", "Amselweg", "Goethestraße", "Wiesenweg", "Buchenweg",
    "Jahnstraße", "Wiesenstraße", "Ahornweg", "Finkenweg", "Eichenweg",
    "Am Sportplatz", "Feldstraße", "Mühlenweg", "Rosenstraße", "Lerchenweg",
    "Drosselweg", "Mühlenstraße", "Talstraße", "Gartenweg", "Industriestraße",
    "Mittelstraße", "Beethovenstraße", "Poststraße", "Waldweg", "Kirchplatz",
    "Meisenweg", "Fliederweg", "Kirchgasse", "Am Bahnhof", "Breslauer Straße",
    "Lessingstraße", "Schloßstraße", "Kiefernweg", "Fasanenweg", "Burgstraße",
    "Neue Straße", "Birkenstraße", "Uhlandstraße", "Kastanienweg",
    "Königsberger Straße", "Tulpenweg", "Schulweg", "Im Winkel", "Mühlweg",
    "Marktplatz", "Parkstraße", "Danziger Straße", "Grüner Weg"
]

def fullname():
    return random.choice([random.choice(de_firstname_male), random.choice(de_firstname_female)])+ " " + random.choice(de_lastname)




def process_model(filename = None):
    if filename is None:
        args = util.Args()
        return args.getValue('gpt4all_model')
    return filename
    

def load_gpt4all(file):
    from gpt4all import GPT4All
    if os.path.isfile(file):
        if '-transient' in sys.argv or '-t' in sys.argv:
            gptj = TransientGpt4All(file)
        else:
            gptj = GPT4All(file)
        return gptj
    else:
        print("Error: Model File Not Found.")
        exit()

class TransientGpt4All:
    model = ''
    def __init__(self, model=None):
        self.model = process_model(model)
    def chat_completion(self, **kwargs):
        gptj = GPT4All(self.model)
        return gptj.chat_completion(**kwargs)

class LlmExecutor(runner.BaseJobExecutor):
    MODULES = ['gpt4all']
    chat = None
    def __init__(self, chat=None):
        self.chat = chat
        if self.chat is None:
            self.chat = load_gpt4all(process_model(None))
    def execute(self, data):
        prompt = data['prompt']
        messages = [{"role": "user", "content": prompt}]
        res = {'success': True}
        res['chat'] = messages
        res['llm'] = True
        if self.chat.__class__.__name__=='GPT4ALL':
            result = self.chat.chat_completion(messages, default_prompt_header=False,  default_prompt_footer=False, streaming=False)
            response = result['choices'][0]['message']['content']
        else:
            response = 'No Backend to answer.'
            res['success'] = False
        res['response'] = response
        res['input'] = data
        return res 



def main():
    print("LLM")
    gptj = load_gpt4all(sys.argv[1])
    executor = LlmExecutor(chat=gptj)
    if len(sys.argv)>2:
        infile = sys.argv[2]
        outfile = sys.argv[3]
        runner = JobRunner(executor)
        if infile == 'rest':
            runner.execute_rest()
        else:
            runner.execute_file(infile, outfile)
    else:
        print("python -m nwebclient.llm model_file")
        print("Usage: model_file infile outfile")
        print("Usage: model_file rest api")
        print("Option: -t --transient fuer TransientGpt4All")
        
if __name__ == '__main__':
    main()