
import json
import tarfile
import xml.etree.ElementTree as ET
from nwebclient import base as b
from nwebclient import web as w

class SkipElement(Exception):
    pass

class MoodleUser:
    id = ''
    username = ''
    firstname = ''
    lastname = ''
    mail = ''
    def __init__(self, xml=None, firstname=None, lastname=None, mail=None):
        if xml is None:
            self.firstname = firstname
            self.lastname = lastname
            self.mail = mail
        else:
            # username firstname lastname
            self.id = xml.attrib['id']
            self.username = xml.find('./username').text
            self.firstname = xml.find('./firstname').text
            self.lastname = xml.find('./lastname').text
    def __str__(self):
        return "{0} {1}".format(self.firstname, self.lastname)


class QuestionAttempt:
    def __init__(self, xml, owner, userid = None):
        self.owner = owner
        self.question = None
        # question_attept
        # Actung kann auch part 1: sein
        #  <rightanswer>Teil 1: nicht kohäsiv; Teil 2: kohäsiv; Teil 3: kohäsiv; Teil 4: gering gekoppelt; Teil 5: gering gekoppelt; Teil 6: stark gekoppelt; Teil 7: kohäsiv</rightanswer>
        #   <responsesummary>Teil 1: nicht kohäsiv; Teil 2: kohäsiv;
        self.rightanswer = xml.find('./rightanswer').text
        self.responsesummary = xml.find('./responsesummary').text
        self.questionid = xml.find('./questionid').text
        self.question = self.owner.questionById(self.questionid)
        self.userid = userid
        # nur steps haben userid
        i = 0
        for step in xml.findall('./steps/step'):
            if i == 0:
                self.userid = step.find('./userid').text
            i += 1
            if step.find('./state').text == 'complete':
                pass
                #<response >
                #< variable >
                #< name > answer < / name >
                #< value > 0 < / value >
                #< / variable >
                #< / response >

    def __str__(self):
        return "QuestionId: {0} ResSummary: {1} Right: {2}  UserId: {3}".format(self.questionid, self.responsesummary, self.rightanswer, self.userid)


class MoodleQuiz:
    attempts = []
    questions = []

    def __init__(self, xml, owner):
        self.owner = owner
        self.attempts = []
        # attempts/attempt/question_usage/question_attempts/question_attempt/steps/step
        for x_attempt in xml.findall('.//attempt'):
            userid = x_attempt.find('./userid').text
            for attempt in x_attempt.findall('.//question_attempt'):
                self.attempts.append(QuestionAttempt(attempt, self.owner, userid))
        # question_instances/question_instance/questionid
        for qi in xml.findall('./question_instances/question_instance'):
            self.questions.append(self.owner.questionById(qi.find('./questionid').text))




class MoodleQuestion:
    name: str = ''
    text: str = ''
    id = None

    def __init__(self, xml, owner):
        self.owner = owner
        try:
            self.name = getattr(xml.find('./name'), 'text', None)
            if 'type' in xml.attrib:
                self.type = xml.attrib['type']
            self.text = xml.find('./questiontext').text
            if 'id' in xml.attrib:
                self.id = xml.attrib['id']
            else:
                self.id = None
        # <answers>
        #   <answer id="11785">
        #       <answertext>&lt;p&gt;Antwort 1&lt;/p&gt;</answertext>\n
        #       <answerformat>1</answerformat>
        #       <fraction>1.0000000</fraction>
        except:
            print("Fehler beim Verarbeiten einer Frage.")
            print(ET.tostring(xml))
            raise SkipElement

    def __str__(self):
        return "ID:" + str(self.id) + " " + self.text

    def attempts(self):
        res = []
        for quiz in self.owner.quizes.values():
            if isinstance(quiz, MoodleQuiz):
                for a in quiz.attempts:
                    if a.questionid == self.id:
                        res.append(a)
        return res


class CorectionFreeText:
    def __init__(self, points=1, full=[], point_for=[]):
        self.points = points
        self.full = points
        self.point_for = point_for

    def is_correct(self, answer):
        return answer.lower() in self.full

    def part_points(self, answer):
        res = 0
        a = answer.lower()
        for part in self.points_for.lower():
            if part in a:
                res += 1
        return res

    def check(self, answer):
        if self.is_correct(answer):
            return self.points
        else:
            return self.part_points()


class MoodleCourse(b.WebPage):
    items = []
    users = []
    quizes = {}
    questions = []

    def __init__(self, filename):
        tar = tarfile.open(filename, "r:gz")
        self.items = []
        self.users = []
        self.quizes = {}
        self.questions = []
        for member in tar.getmembers():
            self.items.append(member)
            print(member.name)
            if member.name == 'users.xml':
                self._set_users(tar, member)
            if member.name == 'questions.xml':
                self._set_questions(tar, member)
        for member in tar.getmembers():
            if member.name.startswith('activities/quiz_'):
                self._add_activiy_quiz(tar, member)

    def _add_activiy_quiz(self, tar, member):
        n = member.name.replace('activities/quiz_', '')
        if not '/' in n:
            #self.quizes[n] = {}
            return
        # inforef.xml grade_history.xml module.xml filters.xml calendar.xml comments.xml quiz.xml grades.xml completion.xml roles.xml
        if n.endswith('quiz.xml'):
            f = tar.extractfile(member)
            if f is not None:
                content = f.read()
                root = ET.fromstring(content)
                self.quizes[n] = MoodleQuiz(root, self)
                # print(content)
                # <question_instances>

    #      <question_instance id="57445">\n
    #	  <slot>1</slot>\n
    #	  <page>1</page>\n
    #      <requireprevious>0</requireprevious>\n
    #	  <questionid>5013</questionid>\n
    #	  <questioncategoryid>$@NULL@$</questioncategoryid>\n
    #      <includingsubcategories>$@NULL@$</includingsubcategories>\n
    #      <maxmark>1.0000000</maxmark>\n
    #	  <tags>\n        </tags>\n
    #  </question_instance>\n
    #  </question_instances>
    def _set_questions(self, tar, member):
        f = tar.extractfile(member)
        if f is not None:
            content = f.read()
            # print(content)
            root = ET.fromstring(content)
            for q in root.findall('.//question'):
                try:
                    self.questions.append(MoodleQuestion(q, self))
                except SkipElement:
                    pass
        # TODO map with id

    def _set_users(self, tar, member):
        f = tar.extractfile(member)
        if f is not None:
            content = f.read()
            # print(content)
            # https://towardsdatascience.com/processing-xml-in-python-elementtree-c8992941efd2
            root = ET.fromstring(content)
            for child in root:
                self.users.append(MoodleUser(child))

    def questionById(self, id):
        for q in self.questions:
            if q.id == id:
                return q
        raise Exception("Question not found.")

    def printQuestions(self):
        for q in self.questions:
            print(q)
            print(q.attempts())
            print("###########################")

    def printAttempts(self):
        for q in self.quizes.values():
            for a in q.attempts:
                print(a)

    def page(self, params={}):
        return "Moodle Course"

#filename = '/mnt/c/Users/root/Downloads/moodle_quiz-activity-194093-quiz194093-20230809-1410.mbz.tar.gz'
#m = MoodleCourse(filename)
#m.printQuestions()
#m.printAttempts()


class OneOfEach:
    """
       Gibt fuer jedes Wort aus einer Kategorie einen Punkt. Aber nie mehr als einen Punkt pro Kategorie.
       Eine Kategorie besteht aus mehreren Wörtern. Taucht ein Wort im Text auf gibt es einen Punkt.

    """
    def __init__(self, categories=[]):
        self.categories = categories
    def check(self, answer):
        punkte = 0
        for c in self.categories:
            contains = False
            for word in c:
                if word.lower() in answer.text.lower():
                    answer.begruendung += '(1P '+word+')'
                    contains = True
                    break
            if contains:
                punkte += 1
        return punkte



class Answer(b.Base):
    _id_counter = 0
    bewertung = None
    def __init__(self, text, user):
        self.bewertung = None
        self.begruendung = ''
        self.text = text
        self.user = user
        Answer._id_counter += 1
        self.id = Answer._id_counter

class Question(b.Base):
    answers = []
    punkte = 1
    text = 'Frage'

    def __init__(self, text=None, punkte=1, check=None):
        self.answers = []
        self.punkte = punkte
        self.check = check
        if text is not None:
            self.text = text

    def append(self, item: Answer):
        #self.addChild(item)
        self.answers.append(item)
    def countAnswers(self, text):
        res = 0
        for a in self.answers:
            if text == a.text:
                res += 1
        return res
    def printTo(self, p: b.Page):
        for a in self.answers:
            p('<div class="answer a'+str(a.id)+'" style="border: 1px #aaa; solid; background-color: #eee; margin-bottom:10px;">')
            p.right(str(a.user), _class='username')
            p.div(a.text, _class='answer_text')
            p.right(str(self.countAnswers(a.text))+"mal")
            if self.check is not None and a.bewertung is None:
                a.bewertung = self.check.check(a)
            p.div(w.input('p', value=str(a.bewertung), _class="punkte", style='width: 50pt;')+'/' + str(self.punkte))
            p.div("Begruendung: "+w.input('b', _class="begruendung", value=a.begruendung))
            for i in range(0, int(self.punkte)+1):
                p(w.button_js(str(i)+'P', 'document.querySelector(".a'+str(a.id)+' .punkte").value = "'+str(i)+'"; '))
            p('</div>')
        p.script(w.js_fn('to_table', [], [
            'var trs= "<tr><th>Teilnehmer</th><th>Punkte</th><th>Antwort</th><th>Begruendung</th></tr>";'
            'document.querySelectorAll(".answer").forEach(r=>{ ',
            '   var punkte = r.querySelector(".punkte").value;',
            '   var username = r.querySelector(".username").textContent;'
            '   var answer_text = r.querySelector(".answer_text").textContent;'
            '   var begruendung = r.querySelector(".begruendung").value;'
            '   trs += "<tr><td>"+username+"</td><td>"+punkte+"</td><td>"+answer_text+"</td><td>"+begruendung+"</td></tr>"'
            '});',
            'var $table = document.createElement("table");',
            '$table.innerHTML = trs; console.log(trs); ',
            'document.body.appendChild($table);'
        ]))
        p(w.button_js("Tabelle", 'to_table();'))


class MoodleJson:
    """

[[[
    "Nachname",       # 0
    "Vorname",        # 1
    "",               # 2
    "email",          # 3
    "Beendet",        # 4
    "21. August 2023  10:38", # 5
    "21. August 2023  12:07", # 6
    "1 Stunde 29 Minuten",    # 7
    "66,50",                  # 8
    "part 1: Scope; part 2: Budget; part 3: Time", #9
    "blen kartenArt und farbe definieren um welche Kart...e Beziehungen also die Kartenränge in jeder Runde ändern.",
    "Man muss abgesehen von der Vergleichsarithmetik zusät... miteinander vergleichen.",
    "b)\n\nstichGewinner(0,0...casets hochskaliert werden."
],[

    """
    rows = []

    questions = [
        Question(text="Projektplanungsdreieck", punkte=3, check=OneOfEach([
            ['Scope', 'Umfang'],
            ['Budget', 'Geld', 'Cost'],
            ['Time', 'Zeit']
        ])),
        Question(), Question(), Question(), Question(),
        Question(), Question(), Question(), Question(), Question(),
        Question(), Question(), Question(), Question(), Question(),
        Question(), Question(), Question(), Question(), Question(),
        Question(), Question(), Question(), Question(), Question(),
        Question(), Question(), Question(), Question(), Question()
    ]

    def __init__(self, file):
        with open(file, 'r') as f:
            table = json.load(f)
            self.rows = table[0]
        for row in self.rows:
            self.processRow(row)

    def processRow(self, row):
        print("Load Row...")
        firstname = row[1]
        lastname = row[0]
        mail = row[3]
        user = MoodleUser(firstname=firstname, lastname=lastname, mail=mail)
        answers = row[9:]
        i = 0
        for answer in answers:
            self.questions[i].append(Answer(answer, user))
            #print(str(i) + ": " + answer)
            i = i + 1
        for q in self.questions:
            q.answers.sort(key=lambda x: x.text)
            print(str(len(q.answers)))



m = MoodleJson('/home/pi/ASE.json')

from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def index():
    p = b.Page()
    p.h1("Fragen")
    i = 0
    for q in m.questions:
        p.div(w.a(q.text, '/question?id='+str(i)))
        i += 1
    return p.simple_page()

@app.route('/question')
def show_question():
    p = b.Page()
    q = m.questions[int(request.args.get('id'))]
    p.h1("Bewertung einer Frage für alle Teilnehmer")
    p.div(q.text)
    q.printTo(p)
    return p.simple_page()


app.run(host='127.0.0.1', port=8888)
