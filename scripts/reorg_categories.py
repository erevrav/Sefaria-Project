#encoding=utf-8
import django
django.setup()
from sefaria.model import *

# root = library.get_toc_tree().get_root()

def moveIndexInto(index, category):
    assert isinstance(index, Index)
    assert isinstance(category, Category)

    index.categories = category.path[:]
    print("Moving - " + index.get_title() + " to " + str(index.categories) + " (moveIndexInto)")
    index.save(override_dependencies=True)

def moveCategoryInto(category, parent):
    """
    c = Category().load({'path': ["Tanaitic", "Minor Tractates"]})
    p = Category().load({"path": ["Talmud", "Bavli"]})
    moveCategoryInto(c, p)

    if parent is None, move to root.

    :param category:
    :param parent:
    :return:
    """
    assert isinstance(category, Category)
    assert isinstance(parent, Category) or parent is None

    old_category_path = category.path[:]
    old_parent_path = category.path[:-1]
    new_parent_path = parent.path[:] if parent else []

    # move all matching categories
    clauses = [{"path." + str(i): cname} for i, cname in enumerate(old_category_path)]
    query = {"$and": clauses}
    old_parent_length = len(old_parent_path)
    for cat in CategorySet(query):
        # replace old_parent_path with new_parent_path
        cat.path = new_parent_path + cat.path[old_parent_length:]
        print("Saving moved category - " + str(cat.path))
        cat.save(override_dependencies=True)

    # move all matching Indexes
    clauses = [{"categories." + str(i): cname} for i, cname in enumerate(old_category_path)]
    query = {"$and": clauses}
    for ind in IndexSet(query):
        assert isinstance(ind, Index)
        ind.categories = new_parent_path + ind.categories[old_parent_length:]
        print("Moving - " + ind.get_title() + " to " + str(ind.categories)  + " (moveCategoryInto)")
        ind.save(override_dependencies=True)

    """
     Handle commentary on parallel trees separately.
     "title": "Commentary of Chida on Tractate Gerim",
     "categories": [
     "Tanaitic",
     "Commentary",
     "Commentary of Chida",
     "Minor Tractates"
     ],
    """

def create_category(path, en=None, he=None):
    c = Category()
    if not Term().load({"name": path[-1]}):
        print("adding term for " + en)
        term = Term()
        term.name = en
        term.add_primary_titles(en, he)
        term.save()
    c.add_shared_term(path[-1])
    c.path = path
    c.lastPath = path[-1]
    print("Creating - {}".format(" / ".join(c.path)))
    c.save(override_dependencies=True)
    return c

### Avot D'Rabbi Natan  -> Midrash Aggadic Midrash
i = library.get_index("Avot D'Rabbi Natan")
p = Category().load({"path": ["Midrash", "Aggadic Midrash"]})
moveIndexInto(i, p)


### Commentaries of ADRN
# e.g:
# ["Tanaitic", "Commentary", "Kisse Rahamim", "Minor Tractates"]
# -> ["Midrash", "Commentary", "Kisse Rahamim"]

adrn_comms = ["Binyan Yehoshua on Avot D'Rabbi Natan",
"Gra's Nuschah on Avot D'Rabbi Natan",
"Haggahot R' Yeshaya Berlin on Avot D'Rabbi Natan",
"Haggahot Ya'avetz on Avot D'Rabbi Natan",
"Kisse Rahamim on Avot D'Rabbi Natan",
"Mitzpeh Etan on Avot D'Rabbi Natan",
"Rishon Letzion on Avot D'Rabbi Natan",
"Tumat Yesharim on Avot D'Rabbi Natan"]

for comm in adrn_comms:
    i = library.get_index(comm)
    name = i.categories[2]
    c = create_category(["Midrash", "Commentary", name])
    moveIndexInto(i, c)

library.rebuild(include_toc=True)
# remove empty categories that had been just ADRN
for p in [
    ["Tanaitic", "Commentary", "Binyan Yehoshua", "Minor Tractates" ],
    ["Tanaitic", "Commentary", "Mitzpeh Etan", "Minor Tractates" ],
    ["Tanaitic", "Commentary", "Tumat Yesharim", "Minor Tractates" ],
    ]:
    c = Category().load({"path": p})
    c.delete()

### The rest of the minor tractates -> Talmud/Bavli
c = Category().load({'path': ["Tanaitic", "Minor Tractates"]})
p = Category().load({"path": ["Talmud", "Bavli"]})
moveCategoryInto(c, p)

### Commentary on minor tractates -> Talmud/Bavli
#        "Tanaitic",         "Commentary",         "Nahalat Yaakov",         "Minor Tractates"
#   =>   "Talmud",      "Bavli",    "Commentary",     "Nahalat Yaakov",  "Minor Tractates",
p = Category().load({"path": ["Talmud", "Bavli", "Commentary"]})
for kid in Category().load({'path': ["Tanaitic", "Commentary"]}).get_toc_object().children:
        c = kid.get_category_object()
        moveCategoryInto(c, p)

### 	Megillat Taanit -> Midrash
i = library.get_index("Megillat Taanit")
c = Category().load({"path": ["Midrash"]})
moveIndexInto(i, c)

### Tosefta -> New top level category
c = Category().load({"path": ["Tanaitic", "Tosefta"]})
moveCategoryInto(c, None)

### Remove Tanaitic
library.rebuild(include_toc=True)
c = Category().load({"path": ["Tanaitic"]})
c.delete()


# Click Talmud -> Commentary of Chida (crash)


# Remove Modern Works
c = Category().load({"path": ["Modern Works", "English Explanation of Mishnah"]})
p = Category().load({"path": ["Mishnah", "Commentary"]})
moveCategoryInto(c, p)


# Shoel uMeshiv to subcat
c = create_category(["Responsa", "Shoel uMeshiv"], en="Shoel uMeshiv", he="שואל ומשיב")
ts = ["Shoel uMeshiv Mahadura I",
"Shoel uMeshiv Mahadura II",
"Shoel uMeshiv Mahadura III",
"Shoel uMeshiv Mahadura IV",
"Shoel uMeshiv Mahadura V",
"Shoel uMeshiv Mahadura VI"]

for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, c)

# Contemporary .. into Halacha
c = create_category(["Halakhah", "Contemporary Halakhic Problems"], en="Contemporary Halakhic Problems", he='בעיות הלכתיות עכשוויות')
ts = [
'Contemporary Halakhic Problems, Vol I',
'Contemporary Halakhic Problems, Vol II',
'Contemporary Halakhic Problems, Vol III',
'Contemporary Halakhic Problems, Vol IV',
'Contemporary Halakhic Problems, Vol V',
'Contemporary Halakhic Problems, Vol VI']
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, c)

# Gray Matter into Halacha
c = create_category(["Halakhah", "Gray Matter"], en="Gray Matter", he='גריי מאטר')
ts = [
'Gray Matter I',
'Gray Matter II',
'Gray Matter III',
'Gray Matter IV',
]
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, c)

# Marei HaBazak to subcat
c = create_category(["Responsa", "B'Mareh HaBazak"], en="B'Mareh HaBazak", he='שו"ת במראה הבזק')
ts = ["B'Mareh HaBazak Volume I",
"B'Mareh HaBazak Volume III",
"B'Mareh HaBazak Volume IV",
"B'Mareh HaBazak Volume IX",
"B'Mareh HaBazak Volume V",
"B'Mareh HaBazak Volume VI",
"B'Mareh HaBazak Volume VII",
"B'Mareh HaBazak Volume VIII"]

for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, c)

# Daf Shevui -> Talmud Commentary
c = create_category(["Talmud", "Bavli", "Commentary", "Daf Shevui"], en="Daf Shevui", he="דף שבועי")
ts = ["Daf Shevui to Avodah Zarah",
 "Daf Shevui to Ketubot",
 "Daf Shevui to Kiddushin",
 "Daf Shevui to Megillah",
 "Daf Shevui to Sukkah"]

for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, c)

#
i = library.get_index("A New Israeli Commentary on Pirkei Avot")
c = Category().load({"path": ["Mishnah", "Commentary"]})   # deeper cat?


c = create_category(["Reference", "Grammar"])
ts = ["Sefer haBachur", "Mahberet Menachem", "Sefat Yeter"]
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, c)

# Jastrow, Klein Dictionary, Otzar Laazei Rashi  => Reference, Dictionary
c = create_category(["Reference", "Dictionary"])
ts = ['Jastrow', 'Klein Dictionary', 'Otzar Laazei Rashi']
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, c)
# Into reference
ts = ["The Jewish Spiritual Heroes", "Ein Zocher", "Devash Lefi", "Midbar Kedemot"]
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, p)


# Rename Philosophy -> Jewish Thought
ph = Term().load({"name": "Philosophy"})
ph.remove_title("מחשבת ישראל", "he")
ph.add_title("פילוסופיה", "he", True, True)
ph.save()

jt = Term().load({"name": "Jewish Thought"})
jt.remove_title("מחשבה יהודית", "he")
jt.add_title("מחשבת ישראל", "he", True, True)
jt.save()

# Change the philo cat itself
phc = Category().load({"path": ["Philosophy"]})
phc.change_key_name("Jewish Thought")
phc.save()


# move all matching categories
for cat in CategorySet({"path.0": "Philosophy"}):
    # replace old_parent_path with new_parent_path
    cat.path = ["Jewish Thought"] + cat.path[1:]
    print("Saving moved category - " + str(cat.path))
    cat.save(override_dependencies=True)

# move all matching Indexes
for ind in IndexSet({"categories.0": "Philosophy"}):
    assert isinstance(ind, Index)
    ind.categories = ["Jewish Thought"] + ind.categories[1:]
    print("Moving - " + ind.get_title() + " to " + str(ind.categories))
    ind.save(override_dependencies=True)


# Move Works of Eliezer Berkovits -> Philosophy
c = Category().load({"path": ["Modern Works", "Works of Eliezer Berkovits"]})
p = Category().load({"path": ["Jewish Thought"]})
moveCategoryInto(c, p)

ts = ['The Midrash of Philo',
 'The Third Beit HaMikdash',
 'Derush Chidushei HaLevana',
 'Halacha and Aggadah',
 'Revealment and Concealment in Language',
 'Against Apion',
 'The Antiquities of the Jews',
 'The War of the Jews',
 'Imrei Binah',
 'Kol HaTor']

for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, p)

p = Category().load({"path": ["Jewish Thought", "Commentary"]})
ts = ["Ali Be'er on Revealment and Concealment in Language",
'Bein HaShitin on Halacha and Aggadah',
'Commentaries on Revealment and Concealment in Language']

for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, p)

p = Category().load({"path": ["Chasidut"]})
ts = ["Flames of Faith"]
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, p)


# Tanakh > Parshanut
p = create_category(["Tanakh", "Parshanut"], "Parshanut", "פרשנות")
ts = ['Depths of Yonah',
 'From David to Destruction']
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, p)

p = create_category(["Tanakh", "Parshanut", "Redeeming Relevance"], "Redeeming Relevance", "פדיון הרלוונטיות")
ts = ['Redeeming Relevance; Deuteronomy',
 'Redeeming Relevance; Exodus',
 'Redeeming Relevance; Genesis',
 'Redeeming Relevance; Numbers']
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, p)

p = Category().load({"path": ["Tanakh", "Commentary"]})
ts = ['Birkat Asher on Torah',
'Chibbah Yeteirah on Torah',
'Footnotes to Kohelet by Bruce Heitler']
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, p)

p = Category().load({"path": ["Talmud", "Bavli", "Commentary"]})
ts = ['Abraham Cohen Footnotes to the English Translation of Masechet Berakhot']
for t in ts:
    i = library.get_index(t)
    moveIndexInto(i, p)



# Reorg Halacha
cat_ivh = create_category(["Halakhah", "Issur v'Heter"], "Issur v'Heter", "איסור והיתר")
books_ivh = ["Issur V'Heter L'Rabbeinu Yerucham",
'Issur veHeter leRashi',
'Torat HaBayit HaAroch',
'Torat HaBayit HaKatzar']

cat_mitzvot = create_category(["Halakhah", "Sifrei Mitzvot"], "Sifrei Mitzvot", "ספרי מצות")
books_mitzvot = ['Sefer Hamitzvot of Rasag',
'Sefer Mitzvot Gadol',
'Sefer Mitzvot Katan',
'Sefer HaMitzvot',
'Sefer HaMitzvot HaKatzar',
'Sefer HaChinukh',
'Minchat Chinukh',
'Sefer Yereim',
'Kitzur Sefer Haredim of Rabbi Elazar Azcari']

cat_mono = create_category(["Halakhah", "Monographs"], "Monographs", "מונוגרפיה")
books_mono = ['Chofetz Chaim',
'The Sabbath Epistle',
'Treasures Hidden in the Sand',
'Bedikat HaSakin',
"Dina d'Garmei",
'Ein HaTekhelet',
'Gevurat Anashim',
'Hilchos Talmud Torah',
'Keset HaSofer',
'Piskei Challah',
'Ptil Tekhelet',
"Sha'ar HaMayim HaAroch",
"Sha'ar HaMayim HaKatzar",
'Shulchan Shel Arba',
'Care of the Critically Ill']

cat_other = create_category(["Halakhah", "Other"], None, None)
books_other = ['Abudarham',
'Avodat HaKodesh',
'Kol Bo',
'Maaseh Rav',
'Machzor Vitry',
'Mateh Efrayim',
'Nehar Misrayim',
'Ohr Zarua',
'Sefer Chasidim',
'Sefer HaParnas',
"Sheiltot d'Rav Achai Gaon",
"Shev Shmat'ta",
'Shulchan Aruch HaRav',
'Simla Chadasha']


for cat, books in [
    (cat_mono, books_mono),
    (cat_mitzvot, books_mitzvot),
    (cat_ivh, books_ivh),
    (cat_other, books_other)
]:
    for book in books:
        i = library.get_index(book)
        moveIndexInto(i, cat)



# remove empty categories
library.rebuild(include_toc=True)
for p in [
        ["Other", "Grammar"],
        ["Other", "Dictionary"],
        ["Other"],
        ["Modern Works", "Commentary"],
        ["Modern Works"]
    ]:
    c = Category().load({"path": p})
    c.delete()



#	Subsections:
#		Rishonim
#		Achronim
#		Modern


# Get rid of "modern commentary" on the sidebar.

# Pin major commentaries on Mishnah


# Tanakh Commentary
# Talmud Commentary
#	Alphabetical  (? really?  not crono?)
