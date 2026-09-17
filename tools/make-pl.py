# -*- coding: utf-8 -*-
"""Génère content/pl.json depuis content/fr.json.
La structure est copiée à l'identique ; seules les chaînes présentes dans T
sont remplacées. Toute chaîne non traduite est signalée en fin d'exécution :
impossible de livrer une page à moitié française sans s'en apercevoir."""
import json, copy, pathlib

SKIP_KEYS = {"type","image","src","id","icon","video","motion","crop",
             "alt","logo","poster","n","lang","locale","base_url","og_image","same_as",
             "youtube","file","class","tone","variant","doc","slug","style","ratio","fit","link","base","widget","start","place"}

T = {
# ------------------------------------------------- textes alternatifs (a11y)
"Affiche du prochain concert de l'Orchestre de Chambre de Wissembourg":
  "Afisz najbliższego koncertu Orkiestry Kameralnej Wissembourg",
"L'Orchestre de Chambre de Wissembourg en concert": "Orkiestra Kameralna Wissembourg podczas koncertu",
"Le Prix du Triangle de Weimar 2024 remis à l'orchestre": "Wręczenie orkiestrze Nagrody Trójkąta Weimarskiego 2024",
"Marc Bender, directeur musical de l'Orchestre de Chambre de Wissembourg":
  "Marc Bender, dyrektor muzyczny Orkiestry Kameralnej Wissembourg",
"Marc Bender, direction artistique": "Marc Bender, dyrekcja artystyczna",
"Partenariat avec la Kreismusikschule Südliche Weinstraße de Landau":
  "Partnerstwo z Kreismusikschule Südliche Weinstraße w Landau",
"Photo de groupe de l'Orchestre de Chambre de Wissembourg au complet sur scène":
  "Zdjęcie grupowe Orkiestry Kameralnej Wissembourg w pełnym składzie na scenie",
# ---------------------------------------------------------------- global
"Wissembourg · Ensemble franco-allemand": "Wissembourg · Zespół francusko-niemiecki",
"<div class=\"demo-ribbon\">Maquette de démonstration — refonte proposée du site de l'Orchestre de Chambre de Wissembourg. Aucun contenu n'est officiel.</div>":
  "<div class=\"demo-ribbon\">Makieta demonstracyjna — propozycja nowej wersji strony Orchestre de Chambre de Wissembourg. Żadna treść nie jest oficjalna.</div>",
"Aller au contenu principal": "Przejdź do treści głównej",
"Navigation principale": "Nawigacja główna",
"Ouvrir le menu": "Otwórz menu",
"Nous soutenir": "Wesprzyj nas",
"Lire la vidéo": "Odtwórz wideo",
"La vidéo n'est chargée qu'après votre clic. Aucun cookie YouTube avant.":
  "Wideo ładuje się dopiero po kliknięciu. Wcześniej żadnych plików cookie YouTube.",
# ---------------------------------------------------------------- nav
"Accueil": "Strona główna",
"Direction": "Dyrygent",
"L'orchestre": "Orkiestra",
"Agenda": "Kalendarz",
"Archives": "Archiwum",
"Presse": "Prasa",
"Contact": "Kontakt",
# ---------------------------------------------------------------- footer
"8 rue de l'Ordre Teutonique<br>67160 Wissembourg — France":
  "8 rue de l'Ordre Teutonique<br>67160 Wissembourg — Francja",
"Association loi locale inscrite au registre du Tribunal d'instance de Haguenau, fondée en décembre 2013.":
  "Stowarzyszenie prawa lokalnego wpisane do rejestru sądu w Haguenau, założone w grudniu 2013 roku.",
"© 2026 Orchestre de Chambre de Wissembourg — Association à but non lucratif":
  "© 2026 Orchestre de Chambre de Wissembourg — stowarzyszenie non profit",
"Site sobre, sans cookie de suivi ni traceur publicitaire.":
  "Strona lekka, bez plików cookie śledzących i bez reklam.",
"Découvrir": "Poznaj", "Participer": "Włącz się", "Suivre": "Obserwuj",
"L'orchestre franco-allemand": "Orkiestra francusko-niemiecka",
"Directeur artistique": "Dyrektor artystyczny",
"Agenda & saisons": "Kalendarz i sezony",
"Revue de presse": "Przegląd prasy",
"Faire un don": "Przekaż darowiznę",
"Adhérer à l'association": "Zostań członkiem stowarzyszenia",
"Mécénat d'entreprise": "Mecenat firmowy",
"Rejoindre l'orchestre": "Dołącz do orkiestry",
"Recevoir le programme": "Otrzymuj program",
# ---------------------------------------------------------------- index
"Orchestre de Chambre de Wissembourg — La musique est notre passion":
  "Orchestre de Chambre de Wissembourg — Muzyka jest naszą pasją",
"Orchestre de chambre franco-allemand basé à Wissembourg : une cinquantaine de musiciens amateurs et professionnels sous la direction de Marc Bender. Lauréat du Prix du Triangle de Weimar 2024.":
  "Francusko-niemiecka orkiestra kameralna z Wissembourga: około pięćdziesięciu muzyków amatorów i zawodowców pod dyrekcją Marca Bendera. Laureat Nagrody Trójkąta Weimarskiego 2024.",
"Prix du Triangle de Weimar 2024": "Nagroda Trójkąta Weimarskiego 2024",
"Partenariat Musikschule Landau": "Partnerstwo z Musikschule Landau",
"Fondé en 2013": "Założona w 2013 roku",
"La musique est notre passion": "Muzyka jest naszą pasją",
"Une cinquantaine de musiciens amateurs et professionnels, français, allemands et polonais, de tous âges et de tous horizons, réunis sous la direction de <strong>Marc Bender</strong> pour faire vivre la musique de chambre de part et d'autre du Rhin.":
  "Około pięćdziesięciu muzyków amatorów i zawodowców — Francuzów, Niemców i Polaków — w każdym wieku i z różnych środowisk, zjednoczonych pod dyrekcją <strong>Marca Bendera</strong>, by muzyka kameralna żyła po obu stronach Renu.",
"Voir les concerts": "Zobacz koncerty",
"Soutenir l'orchestre": "Wesprzyj orkiestrę",
"musiciens": "muzyków",
"année de fondation": "rok założenia",
"pays, un seul orchestre": "kraje, jedna orkiestra",
"saisons de concerts": "sezonów koncertowych",
"À l'affiche": "Na afiszu",
"Prochain rendez-vous": "Najbliższy koncert",
"<p class=\"lead\">Retrouvez l'orchestre pour son prochain concert. Entrée libre, plateau au profit de l'association — la billetterie en ligne permettra bientôt de réserver sa place à l'avance.</p><p class=\"muted\">Les informations de date et de lieu de cette maquette sont à reprendre depuis l'affiche officielle. Dans le site définitif, chaque concert est saisi comme une fiche structurée (date, heure, lieu, programme, tarif) : Google et les agendas culturels peuvent alors l'indexer, ce qui est impossible avec une simple image.</p>":
  "<p class=\"lead\">Zapraszamy na najbliższy koncert orkiestry. Wstęp wolny, zbiórka na rzecz stowarzyszenia — wkrótce będzie można zarezerwować miejsce online.</p><p class=\"muted\">Data i miejsce w tej makiecie są przykładowe i należy je przepisać z oficjalnego afisza. W wersji docelowej każdy koncert jest wpisem o określonej strukturze (data, godzina, miejsce, program, bilety): dzięki temu Google i kalendarze kulturalne mogą go zaindeksować, co przy zwykłym obrazku jest niemożliwe.</p>",
"Tous les concerts": "Wszystkie koncerty",
"Réserver (à activer)": "Rezerwacja (do uruchomienia)",
"L'ensemble": "Zespół",
"Un orchestre sans frontière": "Orkiestra bez granic",
"<p class=\"lead\">L'association OCW a été fondée en 2013 à l'initiative d'élèves motivés, entourés de professeurs passionnés.</p><p>En partenariat avec l'école de musique de Landau depuis 2021, l'ensemble réunit aujourd'hui une cinquantaine de musiciens amateurs et professionnels, de tous âges et de tous horizons, sous la direction de Marc Bender.</p><p>Concerts, tournées, partenariats avec d'autres écoles de musique internationales : chaque projet est une occasion d'enrichissement personnel, culturel et musical — et crée des liens d'amitié durables. Dans l'esprit du Triangle de Weimar, l'ensemble a donné des concerts trinationaux réunissant musiciens français, allemands et polonais.</p><div class=\"bilingual\"><p class=\"eyebrow\">Auf Deutsch</p><p>Musik, eine universelle Sprache, über Grenzen hinweg! Der Verein OCW wurde 2013 auf Initiative motivierter Schülerinnen und Schüler gegründet.</p></div>":
  "<p class=\"lead\">Stowarzyszenie OCW powstało w 2013 roku z inicjatywy zaangażowanych uczniów, wspieranych przez oddanych nauczycieli.</p><p>Od 2021 roku, we współpracy ze szkołą muzyczną w Landau, zespół skupia dziś około pięćdziesięciu muzyków amatorów i zawodowców, w każdym wieku i z różnych środowisk, pod dyrekcją Marca Bendera.</p><p>Koncerty, trasy, partnerstwa z innymi międzynarodowymi szkołami muzycznymi: każdy projekt to okazja do rozwoju osobistego, kulturalnego i muzycznego — i źródło trwałych przyjaźni. W duchu Trójkąta Weimarskiego zespół dał koncerty trójnarodowe, łączące muzyków francuskich, niemieckich i polskich.</p><div class=\"bilingual\"><p class=\"eyebrow\">Auf Deutsch</p><p>Musik, eine universelle Sprache, über Grenzen hinweg! Der Verein OCW wurde 2013 auf Initiative motivierter Schülerinnen und Schüler gegründet.</p></div>",
"Découvrir l'orchestre": "Poznaj orkiestrę",
"Distinction": "Wyróżnienie",
"<p class=\"lead u-measure\">Le Prix du Triangle de Weimar 2024 a été décerné au projet <em>Youth Europe Music</em> par l'association Weimarer Dreieck, en présence du maire de la ville et du Ministerpräsident Bodo Ramelow — une reconnaissance de l'engagement européen porté par l'orchestre.</p>":
  "<p class=\"lead u-measure\">Nagroda Trójkąta Weimarskiego 2024 została przyznana projektowi <em>Youth Europe Music</em> przez stowarzyszenie Weimarer Dreieck, w obecności burmistrza miasta i premiera landu Bodo Ramelowa — to uznanie dla europejskiego zaangażowania orkiestry.</p>",
"Cérémonie du Prix du Triangle de Weimar 2024": "Ceremonia wręczenia Nagrody Trójkąta Weimarskiego 2024",
"Youth Europe Music — extrait de concert": "Youth Europe Music — fragment koncertu",
"Trois façons de faire vivre l'orchestre": "Trzy sposoby, by wesprzeć orkiestrę",
"Assister à un concert": "Przyjdź na koncert",
"Concerts en France et en Allemagne tout au long de la saison, dans les églises, salles et écoles de musique du Rhin supérieur.":
  "Koncerty we Francji i w Niemczech przez cały sezon — w kościołach, salach i szkołach muzycznych Górnego Renu.",
"Voir l'agenda": "Zobacz kalendarz",
"Rejoindre les pupitres": "Dołącz do pulpitów",
"Vous jouez d'un instrument à cordes ou à vent, en amateur ou en professionnel ? L'orchestre accueille de nouveaux musiciens à chaque saison.":
  "Grasz na instrumencie smyczkowym lub dętym, amatorsko albo zawodowo? Orkiestra przyjmuje nowych muzyków w każdym sezonie.",
"Nous écrire": "Napisz do nas",
"Devenir mécène": "Zostań mecenasem",
"Particuliers et entreprises : votre don ouvre droit à une réduction d'impôt de 60 à 66 % et finance partitions, transports et location de salles.":
  "Osoby prywatne i firmy: darowizna daje prawo do ulgi podatkowej od 60 do 66 % (prawo francuskie) i finansuje nuty, transport oraz wynajem sal.",
"Ils nous soutiennent": "Wspierają nas",
"Partenaires et mécènes": "Partnerzy i mecenasi",
"<p class=\"lead\">Nous remercions chaleureusement nos sponsors, dont le soutien rend possible chaque saison de concerts.</p>":
  "<p class=\"lead\">Serdecznie dziękujemy naszym sponsorom, dzięki którym każdy sezon koncertowy jest możliwy.</p>",
"Ville de Wissembourg": "Miasto Wissembourg",
"Partenaire": "Partner",
"Devenir partenaire": "Zostań partnerem",
"Newsletter": "Newsletter",
"Ne manquez plus un concert": "Nie przegap żadnego koncertu",
"Recevez le programme de la saison et le rappel des concerts, deux à quatre fois par an. Désinscription en un clic, aucune donnée transmise à des tiers.":
  "Otrzymuj program sezonu i przypomnienia o koncertach, dwa do czterech razy w roku. Wypisanie jednym kliknięciem, żadnych danych przekazywanych osobom trzecim.",
"Recevoir le programme par mail": "Otrzymuj program e-mailem",
"Suivre sur Facebook": "Obserwuj na Facebooku",
# ---------------------------------------------------------------- direction
"Marc Bender, directeur artistique — Orchestre de Chambre de Wissembourg":
  "Marc Bender, dyrektor artystyczny — Orchestre de Chambre de Wissembourg",
"Marc Bender dirige l'Orchestre de Chambre de Wissembourg depuis 2010. Violoniste à la Philharmonie de Baden-Baden, formé à Strasbourg, Stuttgart et Londres.":
  "Marc Bender kieruje Orkiestrą Kameralną Wissembourg od 2010 roku. Skrzypek Filharmonii Baden-Baden, kształcony w Strasburgu, Stuttgarcie i Londynie.",
"Direction artistique": "Dyrekcja artystyczna",
"Violoniste et chef d'orchestre. Il dirige l'Orchestre de Chambre de Wissembourg depuis 2010 et porte le projet franco-allemand de l'ensemble.":
  "Skrzypek i dyrygent. Od 2010 roku kieruje Orkiestrą Kameralną Wissembourg i rozwija jej francusko-niemiecki projekt.",
"Portrait": "Sylwetka",
"Un violon comme trait d'union": "Skrzypce jako łącznik",
"<p class=\"lead\">Marc Bender étudie le violon au Conservatoire de Strasbourg, dans les classes d'Odile Meyer-Siat puis de Haïk Davtian.</p><p>Il se perfectionne ensuite à la Musikhochschule de Stuttgart auprès de Kolja Lessing, puis au Royal College of Music de Londres auprès de Levon Chilingirian.</p><p>Il a joué au sein de l'English Chamber Orchestra, du Heilbronner Kammerorchester, du Tübinger Kammerorchester et de l'Orchestre Philharmonique de Strasbourg, et s'est produit en concert dans toute l'Europe et en Asie. Il est aujourd'hui violoniste à la Philharmonie de Baden-Baden.</p><p>Depuis 2010, il assure la direction musicale de l'Orchestre de Chambre de Wissembourg, dont il a accompagné la transformation en ensemble franco-allemand aux côtés de l'école de musique de Landau.</p>":
  "<p class=\"lead\">Marc Bender studiował skrzypce w Konserwatorium w Strasburgu, w klasach Odile Meyer-Siat, a następnie Haïka Davtiana.</p><p>Kształcił się dalej w Musikhochschule w Stuttgarcie u Kolji Lessinga, a potem w Royal College of Music w Londynie u Levona Chilingiriana.</p><p>Grał w English Chamber Orchestra, Heilbronner Kammerorchester, Tübinger Kammerorchester oraz w Orkiestrze Filharmonicznej w Strasburgu, występował w całej Europie i w Azji. Dziś jest skrzypkiem Filharmonii Baden-Baden.</p><p>Od 2010 roku sprawuje kierownictwo muzyczne Orkiestry Kameralnej Wissembourg i towarzyszył jej przemianie w zespół francusko-niemiecki u boku szkoły muzycznej w Landau.</p>",
"Profil LinkedIn": "Profil LinkedIn",
"à la direction de l'orchestre": "lat na czele orkiestry",
"conservatoires et académies": "konserwatoria i akademie",
"orchestres professionnels": "orkiestry zawodowe",
"continents en tournée": "kontynenty w trasie",
"Parcours": "Droga zawodowa",
"Formation et carrière": "Wykształcenie i kariera",
"Formation": "Studia",
"Conservatoire de Strasbourg": "Konserwatorium w Strasburgu",
"Violon, dans les classes d'Odile Meyer-Siat puis de Haïk Davtian.":
  "Skrzypce, w klasach Odile Meyer-Siat, a następnie Haïka Davtiana.",
"Perfectionnement": "Studia podyplomowe",
"Musikhochschule de Stuttgart": "Musikhochschule w Stuttgarcie",
"Auprès de Kolja Lessing.": "U Kolji Lessinga.",
"Royal College of Music, Londres": "Royal College of Music, Londyn",
"Auprès de Levon Chilingirian.": "U Levona Chilingiriana.",
"Carrière d'orchestre": "Kariera orkiestrowa",
"English Chamber Orchestra, Heilbronn, Tübingen, Strasbourg": "English Chamber Orchestra, Heilbronn, Tybinga, Strasburg",
"Violoniste au sein du Heilbronner Kammerorchester, du Tübinger Kammerorchester et de l'Orchestre Philharmonique de Strasbourg. Concerts dans toute l'Europe et en Asie.":
  "Skrzypek Heilbronner Kammerorchester, Tübinger Kammerorchester i Orkiestry Filharmonicznej w Strasburgu. Koncerty w całej Europie i w Azji.",
"Depuis 2010": "Od 2010 roku",
"Direction de l'Orchestre de Chambre de Wissembourg": "Kierownictwo Orkiestry Kameralnej Wissembourg",
"Direction musicale de l'ensemble et développement du projet franco-allemand avec l'école de musique de Landau.":
  "Kierownictwo muzyczne zespołu i rozwój projektu francusko-niemieckiego ze szkołą muzyczną w Landau.",
"Aujourd'hui": "Obecnie",
"Philharmonie de Baden-Baden": "Filharmonia Baden-Baden",
"Violoniste au sein de l'orchestre.": "Skrzypek w orkiestrze.",
"La musique, un langage universel, au-delà des frontières.": "Muzyka, język uniwersalny, ponad granicami.",
"Devise de l'Orchestre de Chambre de Wissembourg": "Dewiza Orkiestry Kameralnej Wissembourg",
"Travailler avec l'orchestre": "Współpraca z orkiestrą",
"Projet de concert, invitation d'un soliste, partenariat avec une école de musique ou une institution : la direction artistique répond directement aux propositions.":
  "Projekt koncertu, zaproszenie solisty, partnerstwo ze szkołą muzyczną lub instytucją: dyrekcja artystyczna odpowiada na propozycje bezpośrednio.",
"Écrire à l'orchestre": "Napisz do orkiestry",
# ---------------------------------------------------------------- orchestre
"L'orchestre franco-allemand — Orchestre de Chambre de Wissembourg":
  "Orkiestra francusko-niemiecka — Orchestre de Chambre de Wissembourg",
"Un orchestre de chambre franco-allemand de cinquante musiciens, dirigé par Marc Bender, en partenariat avec l'école de musique de Landau depuis 2021.":
  "Francusko-niemiecka orkiestra kameralna licząca pięćdziesięciu muzyków, pod dyrekcją Marca Bendera, we współpracy ze szkołą muzyczną w Landau od 2021 roku.",
"La musique, un langage universel, au-delà des frontières. — Musik, eine universelle Sprache, über Grenzen hinweg.":
  "Muzyka, język uniwersalny, ponad granicami. — Musik, eine universelle Sprache, über Grenzen hinweg.",
"L'ensemble au complet": "Zespół w pełnym składzie",
"Cinquante musiciens, trois pays": "Pięćdziesięciu muzyków, trzy kraje",
"L'Orchestre de Chambre de Wissembourg réuni sur scène, musiciens français, allemands et polonais confondus, sous la direction de Marc Bender.":
  "Orkiestra Kameralna Wissembourg na scenie — muzycy francuscy, niemieccy i polscy razem, pod dyrekcją Marca Bendera.",
"<p class=\"lead\">L'objectif d'une telle structure est de partager ensemble et de façon pérenne le plaisir de jouer d'un instrument dans une ambiance conviviale, et d'encourager une ouverture vers d'autres pays — Allemagne, Pologne… La musique étant un langage universel.</p><p>L'orchestre franco-allemand propose divers projets tout au long de l'année : concerts, tournées, partenariats avec d'autres écoles de musique internationales. Ces expériences apportent un enrichissement personnel, relationnel, culturel et musical, et créent des liens d'amitié durables.</p><p>L'association OCW (Orchestre de Chambre de Wissembourg) a été fondée en 2013, à l'initiative d'élèves motivés eux-mêmes entourés de professeurs passionnés. Cet ensemble, en partenariat avec l'école de musique de Landau depuis 2021, compte aujourd'hui une cinquantaine de musiciens amateurs et professionnels, de tous âges et de tous horizons, sous la direction de Marc Bender.</p><div class=\"bilingual\"><p class=\"eyebrow\">Auf Deutsch</p><p>Das Ziel einer solchen Struktur ist, gemeinsam und nachhaltig die Freude am Spielen eines Instruments in einer freundlichen Atmosphäre zu teilen und auch die Offenheit gegenüber anderen Ländern (Deutschland, Polen…) zu fördern. Musik ist eine universelle Sprache!</p><p>Das deutsch-französische Orchester bietet daher das ganze Jahr über verschiedene Projekte an, wie Konzerte, Tourneen und Partnerschaften mit anderen internationalen Musikschulen.</p></div>":
  "<p class=\"lead\">Celem takiej struktury jest wspólne i trwałe dzielenie się radością gry na instrumencie w przyjaznej atmosferze oraz otwieranie się na inne kraje — Niemcy, Polskę… Muzyka jest bowiem językiem uniwersalnym.</p><p>Orkiestra francusko-niemiecka realizuje przez cały rok różne projekty: koncerty, trasy, partnerstwa z innymi międzynarodowymi szkołami muzycznymi. Te doświadczenia wzbogacają osobiście, kulturalnie i muzycznie, a także tworzą trwałe przyjaźnie.</p><p>Stowarzyszenie OCW (Orchestre de Chambre de Wissembourg) powstało w 2013 roku z inicjatywy zaangażowanych uczniów, wspieranych przez oddanych nauczycieli. Zespół, współpracujący ze szkołą muzyczną w Landau od 2021 roku, liczy dziś około pięćdziesięciu muzyków amatorów i zawodowców, w każdym wieku i z różnych środowisk, pod dyrekcją Marca Bendera.</p><div class=\"bilingual\"><p class=\"eyebrow\">Auf Deutsch</p><p>Das Ziel einer solchen Struktur ist, gemeinsam und nachhaltig die Freude am Spielen eines Instruments in einer freundlichen Atmosphäre zu teilen und auch die Offenheit gegenüber anderen Ländern (Deutschland, Polen…) zu fördern. Musik ist eine universelle Sprache!</p><p>Das deutsch-französische Orchester bietet daher das ganze Jahr über verschiedene Projekte an, wie Konzerte, Tourneen und Partnerschaften mit anderen internationalen Musikschulen.</p></div>",
"Marc Bender": "Marc Bender",
"<p class=\"lead\">Violoniste formé à Strasbourg, Stuttgart et Londres, aujourd'hui à la Philharmonie de Baden-Baden. Il dirige l'orchestre depuis 2010.</p>":
  "<p class=\"lead\">Skrzypek kształcony w Strasburgu, Stuttgarcie i Londynie, dziś w Filharmonii Baden-Baden. Kieruje orkiestrą od 2010 roku.</p>",
"Découvrir le directeur artistique": "Poznaj dyrektora artystycznego",
"Les musiciens": "Muzycy",
"Les pupitres": "Pulpity",
"<p class=\"lead u-measure\">Cordes, vents et percussions : l'orchestre réunit une cinquantaine d'instrumentistes français et allemands. La liste nominative des musiciens par pupitre est en cours de constitution et sera publiée ici.</p>":
  "<p class=\"lead u-measure\">Smyczki, instrumenty dęte i perkusja: orkiestra skupia około pięćdziesięciu instrumentalistów z Francji, Niemiec i Polski. Imienna lista muzyków według pulpitów jest w opracowaniu i zostanie tu opublikowana.</p>",
"Violons I & II": "Skrzypce I i II",
"Altos": "Altówki",
"Violoncelles": "Wiolonczele",
"Contrebasses": "Kontrabasy",
"L'association": "Stowarzyszenie",
"Une association au service de la formation musicale": "Stowarzyszenie w służbie edukacji muzycznej",
"<p>L'association <strong>Orchestre de Chambre de Wissembourg</strong> a été créée en décembre 2013 pour poursuivre le développement de la formation musicale. Elle est inscrite au registre du Tribunal d'instance de Haguenau.</p><h3>Le bureau</h3><ul class=\"infolist\"><li><strong>Marc Bender</strong>Directeur musical</li><li><strong>William Hege</strong>Président</li><li><strong>Adeline Hirschler</strong>Trésorière</li><li><strong>Gabrièle Hege</strong>Secrétaire</li></ul>":
  "<p>Stowarzyszenie <strong>Orchestre de Chambre de Wissembourg</strong> powstało w grudniu 2013 roku, aby dalej rozwijać edukację muzyczną. Jest wpisane do rejestru sądu w Haguenau.</p><h3>Zarząd</h3><ul class=\"infolist\"><li><strong>Marc Bender</strong>Dyrektor muzyczny</li><li><strong>William Hege</strong>Prezes</li><li><strong>Adeline Hirschler</strong>Skarbniczka</li><li><strong>Gabrièle Hege</strong>Sekretarz</li></ul>",
"Vous jouez d'un instrument ?": "Grasz na instrumencie?",
"L'orchestre accueille chaque saison de nouveaux musiciens, amateurs confirmés comme professionnels, français comme allemands. Écrivez-nous : nous vous indiquerons les prochaines répétitions.":
  "W każdym sezonie orkiestra przyjmuje nowych muzyków — zarówno doświadczonych amatorów, jak i zawodowców, z Francji, Niemiec i Polski. Napisz do nas, a podamy terminy najbliższych prób.",
# ---------------------------------------------------------------- agenda
"Agenda & saisons — Orchestre de Chambre de Wissembourg":
  "Kalendarz i sezony — Orchestre de Chambre de Wissembourg",
"Les concerts à venir de l'Orchestre de Chambre de Wissembourg et les archives des quatorze saisons depuis 2011.":
  "Nadchodzące koncerty Orkiestry Kameralnej Wissembourg oraz archiwum czternastu sezonów od 2011 roku.",
"Saison en cours": "Bieżący sezon",
"Agenda des concerts": "Kalendarz koncertów",
"Concerts en France et en Allemagne, dans les églises, salles et écoles de musique du Rhin supérieur. Entrée libre ou plateau, sauf mention contraire.":
  "Koncerty we Francji i w Niemczech — w kościołach, salach i szkołach muzycznych Górnego Renu. Wstęp wolny lub zbiórka, o ile nie zaznaczono inaczej.",
"Prochainement": "Wkrótce",
"Concerts à venir": "Nadchodzące koncerty",
"<p class=\"lead\">Exemple de rendu : dans le site définitif, chaque concert est une fiche structurée — donc indexable par Google, exportable vers les agendas culturels et rappelable par newsletter.</p>":
  "<p class=\"lead\">Przykład wyglądu: w wersji docelowej każdy koncert jest wpisem o określonej strukturze — zaindeksowanym przez Google, możliwym do wyeksportowania do kalendarzy kulturalnych i do przypomnienia w newsletterze.</p>",
"Oct.": "paź.", "Nov.": "lis.", "Jan.": "sty.",
"nov.": "lis.",
# --- saison 2026-2027 : Petite Messe solennelle de Rossini, quatre dates ---
"<p class=\"lead\">Quatre concerts autour d'une même œuvre : la <em>Petite Messe solennelle</em> de Rossini. Deux dates sont arrêtées, deux restent à caler.</p>":
  "<p class=\"lead\">Cztery koncerty wokół jednego dzieła: <em>Petite Messe solennelle</em> Rossiniego. Dwie daty są ustalone, dwie pozostają do uzgodnienia.</p>",
"Petite Messe solennelle — Rossini": "Petite Messe solennelle — Rossini",
"Samedi 7 novembre, 19 h · Église Saint-Jean, Wissembourg · Entrée libre, plateau":
  "Sobota 7 listopada, godz. 19 · Église Saint-Jean, Wissembourg (Francja) · Wstęp wolny, zbiórka",
"Dimanche 8 novembre, 17 h · St. Johannes, Landau (Allemagne) · Entrée libre, plateau":
  "Niedziela 8 listopada, godz. 17 · St. Johannes, Landau (Niemcy) · Wstęp wolny, zbiórka",
"Munchhausen / Mothern · Date et horaire en cours de calage":
  "Munchhausen / Mothern · Data i godzina w trakcie ustalania",
"Strasbourg · Lieu et date en cours de calage":
  "Strasburg · Miejsce i data w trakcie ustalania",
"Date à fixer": "Data do ustalenia",
"<p><strong>Informations musiciens.</strong> Raccord le samedi 7 novembre à partir de 15 h à l'église Saint-Jean ; Anspielprobe le dimanche 8 novembre à 14 h 30 à Landau.</p>":
  "<p><strong>Informacje dla muzyków.</strong> Próba w sobotę 7 listopada od godz. 15 w kościele Saint-Jean; Anspielprobe w niedzielę 8 listopada o godz. 14.30 w Landau.</p>",
"<p class=\"lead\">Samedi 7 novembre à 19 h, église Saint-Jean à Wissembourg : l'orchestre donne la <em>Petite Messe solennelle</em> de Rossini, reprise le lendemain à 17 h à St. Johannes de Landau. Entrée libre, plateau au profit de l'association.</p><p class=\"muted\">L'affiche reste à remplacer par celle de ce concert. Dans le site définitif, chaque concert est saisi comme une fiche structurée (date, heure, lieu, programme, tarif) : Google et les agendas culturels peuvent alors l'indexer, ce qui est impossible avec une simple image.</p>":
  "<p class=\"lead\">W sobotę 7 listopada o godz. 19, w kościele Saint-Jean w Wissembourgu, orkiestra wykona <em>Petite Messe solennelle</em> Rossiniego; nazajutrz o godz. 17 w St. Johannes w Landau. Wstęp wolny, zbiórka na rzecz stowarzyszenia.</p><p class=\"muted\">Afisz trzeba jeszcze zastąpić afiszem tego koncertu. W wersji docelowej każdy koncert jest wpisem o określonej strukturze (data, godzina, miejsce, program, bilety): dzięki temu Google i kalendarze kulturalne mogą go zaindeksować, co przy zwykłym obrazku jest niemożliwe.</p>",
"Concert d'ouverture de saison": "Koncert inaugurujący sezon",
"20 h 00 · Église Saints-Pierre-et-Paul, Wissembourg · Programme à confirmer · Entrée libre, plateau":
  "20.00 · Kościół św. Piotra i Pawła, Wissembourg · Program do potwierdzenia · Wstęp wolny, zbiórka",
"Réserver": "Rezerwuj",
"Deutsch-Französisches Konzert": "Deutsch-Französisches Konzert",
"17 h 00 · Musikschule Landau (Allemagne) · En partenariat avec l'école de musique de Landau":
  "17.00 · Musikschule Landau (Niemcy) · We współpracy ze szkołą muzyczną w Landau",
"Concert du Nouvel An": "Koncert noworoczny",
"16 h 00 · Salle de la Nef, Wissembourg · Programme viennois":
  "16.00 · Salle de la Nef, Wissembourg · Program wiedeński",
"<p><strong>À compléter par l'association.</strong> Ces trois dates sont des exemples de mise en forme, destinés à montrer le rendu. Elles sont à remplacer par le programme réel de la saison.</p>":
  "<p><strong>Do uzupełnienia przez stowarzyszenie.</strong> Te trzy daty są przykładami formatowania, pokazującymi wygląd strony. Należy je zastąpić rzeczywistym programem sezonu.</p>",
# ---------------------------------------------------------------- archives
"Archives — Orchestre de Chambre de Wissembourg": "Archiwum — Orchestre de Chambre de Wissembourg",
"Quatorze saisons de concerts, les affiches, les photos et les vidéos de l'Orchestre de Chambre de Wissembourg depuis 2011.":
  "Czternaście sezonów koncertowych: afisze, zdjęcia i nagrania Orkiestry Kameralnej Wissembourg od 2011 roku.",
"Mémoire de l'orchestre": "Pamięć orkiestry",
"Quatorze saisons de concerts depuis 2011, en France comme en Allemagne. Affiches, photographies et captations vidéo : tout est conservé et remis en ligne, sous une forme enfin consultable.":
  "Czternaście sezonów koncertowych od 2011 roku, we Francji i w Niemczech. Afisze, fotografie i nagrania wideo: wszystko zachowane i ponownie udostępnione, wreszcie w czytelnej formie.",
"Saison 2024-2025": "Sezon 2024-2025",
"Les affiches de la dernière saison": "Afisze ostatniego sezonu",
"<p class=\"lead\">Chaque saison dispose de sa galerie. Les affiches sont réaffichées en pleine page, optimisées pour se charger vite, y compris sur un téléphone en 4G.</p>":
  "<p class=\"lead\">Każdy sezon ma własną galerię. Afisze są pokazywane na pełnej stronie i zoptymalizowane tak, by ładowały się szybko, także na telefonie w sieci 4G.</p>",
"Concert de mai 2025": "Koncert, maj 2025",
"Concert de printemps 2025": "Koncert wiosenny 2025",
"Deutsch-Französisches Konzert — janvier 2025": "Deutsch-Französisches Konzert — styczeń 2025",
"Concert d'octobre 2024": "Koncert, październik 2024",
"Concert d'automne 2024": "Koncert jesienny 2024",
"Captations": "Nagrania",
"Les concerts en vidéo": "Koncerty na wideo",
"<p class=\"lead u-measure\">Les vidéos restent hébergées sur la chaîne de l'orchestre et sont intégrées ici. Rien n'est chargé tant que vous n'avez pas cliqué : aucun cookie tiers à l'ouverture de la page.</p>":
  "<p class=\"lead u-measure\">Nagrania pozostają na kanale orkiestry i są tu osadzone. Nic nie ładuje się, dopóki nie klikniesz: żadnych plików cookie osób trzecich przy otwarciu strony.</p>",
"Toutes les saisons": "Wszystkie sezony",
"2011 à aujourd'hui": "Od 2011 roku do dziś",
"<p class=\"lead\">Les pages détaillées de chaque saison, reprises de l'ancien site. Elles seront intégrées ici au fil de la migration.</p>":
  "<p class=\"lead\">Szczegółowe strony każdego sezonu, przeniesione ze starej witryny. Będą tu dodawane w miarę postępu migracji.</p>",
"Le fonds photographique": "Zbiór fotograficzny",
"Treize ans d'images, conservés pour de bon": "Trzynaście lat zdjęć, zachowanych na dobre",
"<p class=\"lead\">La médiathèque accumulée depuis 2013 représente près de 3 Go : photographies de concert, affiches, scans de presse, programmes.</p><p>Ce fonds est intégralement récupéré et conservé. Il vit désormais à deux endroits, chacun avec son rôle :</p><div class=\"note\"><p><strong>Sur le site</strong> — une sélection par saison, en résolution adaptée à l'écran. Les images se chargent en une fraction de seconde là où les fichiers d'origine, jusqu'à 5 000 pixels de large, pénalisaient chaque visite.</p></div><div class=\"note u-mt-16\"><p><strong>Hors du site</strong> — l'intégralité des originaux en haute définition, sur l'espace de stockage de l'association et sur une sauvegarde physique. Un site web sert à montrer, pas à archiver : les originaux restent disponibles pour la presse, les affiches et les tirages.</p></div><p class=\"muted u-mt-20\">Cette récupération est à faire tant que l'ancien hébergement est actif. Une fois l'abonnement résilié, les fichiers ne sont plus téléchargeables.</p>":
  "<p class=\"lead\">Zbiór zgromadzony od 2013 roku to blisko 3 GB: zdjęcia koncertowe, afisze, skany prasowe, programy.</p><p>Całość została odzyskana i zachowana. Żyje teraz w dwóch miejscach, każde w swojej roli:</p><div class=\"note\"><p><strong>Na stronie</strong> — wybór z każdego sezonu, w rozdzielczości dopasowanej do ekranu. Zdjęcia ładują się w ułamku sekundy, podczas gdy pliki źródłowe, szerokie nawet na 5000 pikseli, obciążały każdą wizytę.</p></div><div class=\"note u-mt-16\"><p><strong>Poza stroną</strong> — komplet oryginałów w wysokiej rozdzielczości, w przestrzeni dyskowej stowarzyszenia i na kopii fizycznej. Strona internetowa służy do pokazywania, nie do archiwizacji: oryginały pozostają dostępne dla prasy, na afisze i do druku.</p></div><p class=\"muted u-mt-20\">Odzyskanie plików trzeba wykonać, dopóki stary hosting działa. Po rozwiązaniu abonamentu nie będzie już można ich pobrać.</p>",
# ---------------------------------------------------------------- presse
"Revue de presse — Orchestre de Chambre de Wissembourg": "Przegląd prasy — Orchestre de Chambre de Wissembourg",
"Articles de presse consacrés à l'Orchestre de Chambre de Wissembourg et à son directeur musical Marc Bender.":
  "Artykuły prasowe poświęcone Orkiestrze Kameralnej Wissembourg i jej dyrektorowi muzycznemu Marcowi Benderowi.",
"Espace presse": "Strefa prasowa",
"Ils parlent de nous": "Piszą o nas",
"Articles parus dans la presse régionale française et allemande. Journalistes : les visuels haute définition et le dossier de presse sont disponibles sur simple demande.":
  "Artykuły opublikowane we francuskiej i niemieckiej prasie regionalnej. Dziennikarze: zdjęcia w wysokiej rozdzielczości i materiały prasowe udostępniamy na życzenie.",
"Sélection": "Wybór",
"Articles": "Artykuły",
"Dernières Nouvelles d'Alsace · 22 mai 2024": "Dernières Nouvelles d'Alsace · 22 maja 2024",
"Un concert trinational à Wissembourg": "Koncert trójnarodowy w Wissembourgu",
"L'orchestre réunit musiciens français, allemands et polonais pour un concert placé sous le signe de l'amitié européenne.":
  "Orkiestra łączy muzyków francuskich, niemieckich i polskich w koncercie pod znakiem europejskiej przyjaźni.",
"Lire l'article (PDF)": "Przeczytaj artykuł (PDF)",
"Marc Bender, le violon comme trait d'union": "Marc Bender, skrzypce jako łącznik",
"Portrait du directeur musical de l'orchestre, violoniste à la Philharmonie de Baden-Baden.":
  "Sylwetka dyrektora muzycznego orkiestry, skrzypka Filharmonii Baden-Baden.",
"Presse régionale · septembre 2022": "Prasa regionalna · wrzesień 2022",
"L'orchestre fait sa rentrée": "Orkiestra wraca po wakacjach",
"Retour sur le concert de rentrée de l'ensemble franco-allemand.":
  "Relacja z inauguracyjnego koncertu zespołu francusko-niemieckiego.",
"Presse régionale · janvier 2020": "Prasa regionalna · styczeń 2020",
"L'orchestre ouvre l'année devant une salle comble.": "Orkiestra otwiera rok przy komplecie publiczności.",
"Contact presse": "Kontakt dla prasy",
"Dossier de presse": "Materiały prasowe",
"<div class=\"note\"><p>Photographies libres de droits en haute définition, biographie du chef, historique de l'association et visuels des affiches : contactez-nous et nous vous transmettons l'ensemble sous 48 h.</p></div>":
  "<div class=\"note\"><p>Zdjęcia w wysokiej rozdzielczości do swobodnego wykorzystania, biografia dyrygenta, historia stowarzyszenia i projekty afiszy: napisz do nas, a prześlemy komplet w ciągu 48 godzin.</p></div>",
"Demander le dossier de presse": "Poproś o materiały prasowe",
# ---------------------------------------------------------------- soutenir
"Nous soutenir — Orchestre de Chambre de Wissembourg": "Wesprzyj nas — Orchestre de Chambre de Wissembourg",
"Don, adhésion, mécénat d'entreprise : trois façons de soutenir l'Orchestre de Chambre de Wissembourg, avec réduction d'impôt.":
  "Darowizna, członkostwo, mecenat firmowy: trzy sposoby wsparcia Orkiestry Kameralnej Wissembourg, z ulgą podatkową.",
"Mécénat & dons": "Mecenat i darowizny",
"Faire vivre l'orchestre": "Spraw, by orkiestra żyła",
"Partitions, location de salles, transport des instruments, déplacements transfrontaliers : chaque saison a un coût. L'orchestre est une association entièrement bénévole — votre soutien va directement à la musique.":
  "Nuty, wynajem sal, transport instrumentów, przejazdy przez granicę: każdy sezon kosztuje. Orkiestra to stowarzyszenie w pełni wolontariackie — Twoje wsparcie trafia wprost do muzyki.",
"Ponctuel ou mensuel, à partir de 10 €. Reçu fiscal automatique : un don de 100 € ne vous coûte réellement que 34 € après réduction d'impôt de 66 %.":
  "Jednorazowo lub co miesiąc, od 10 €. Automatyczne potwierdzenie podatkowe: darowizna 100 € kosztuje realnie 34 € po uldze podatkowej 66 % (prawo francuskie).",
"Donner en ligne": "Przekaż online",
"Devenez membre, recevez le programme en avant-première et prenez part à l'assemblée générale. Adhésion annuelle à partir de 20 €.":
  "Zostań członkiem, otrzymuj program w przedpremierowo i bierz udział w walnym zgromadzeniu. Składka roczna od 20 €.",
"Adhérer": "Dołącz",
"60 % de réduction d'impôt sur les sociétés, dans la limite de 0,5 ‰ du chiffre d'affaires. Votre logo sur les affiches, le programme et ce site, avec un lien vers votre entreprise.":
  "60 % ulgi w podatku dochodowym od osób prawnych, do 0,5 ‰ obrotu (prawo francuskie). Twoje logo na afiszach, w programie i na tej stronie, z linkiem do firmy.",
"Nous contacter": "Skontaktuj się z nami",
"Comment ça marche": "Jak to działa",
"Un paiement en ligne gratuit pour l'association": "Płatności online bezpłatne dla stowarzyszenia",
"<p class=\"lead\">Dons, adhésions et billetterie passeront par <strong>HelloAsso</strong>, la plateforme de référence des associations françaises : 0 % de commission, reçu fiscal généré automatiquement, hébergement en France et conformité RGPD.</p><div class=\"note\"><p><strong>Compte ouvert, campagne à publier.</strong> L'association dispose déjà de sa page HelloAsso. Il reste au bureau à y créer le formulaire de don : les boutons ci-dessus s'y brancheront sans nouvelle intervention sur le site. En attendant, ils mènent à la page de l'association.</p></div><h3 id=\"billetterie\">Billetterie</h3><p>La billetterie en ligne permet de réserver sa place à l'avance, de connaître l'affluence attendue et d'envoyer un rappel automatique la veille du concert. Elle reste compatible avec l'entrée libre : on réserve gratuitement, et le plateau se fait sur place.</p><h3 id=\"adhesion\">Adhésion</h3><p>L'adhésion soutient le fonctionnement courant de l'association et donne voix au chapitre lors de l'assemblée générale annuelle.</p><h3 id=\"mecenat\">Mécénat d'entreprise</h3><p>Le mécénat relève de la loi Aillagon du 1<sup>er</sup> août 2003 : 60 % du montant du don est déductible de l'impôt sur les sociétés, dans la limite de 0,5 ‰ du chiffre d'affaires hors taxes, avec report possible sur cinq exercices. En contrepartie, l'entreprise bénéficie d'une visibilité (logo, mention, invitations) plafonnée à 25 % du montant du don.</p>":
  "<p class=\"lead\">Darowizny, składki członkowskie i bilety będą obsługiwane przez <strong>HelloAsso</strong>, wiodącą platformę francuskich stowarzyszeń: 0 % prowizji, automatyczne potwierdzenie podatkowe, hosting we Francji i zgodność z RODO.</p><div class=\"note\"><p><strong>Konto założone, kampania do opublikowania.</strong> Stowarzyszenie ma już swoją stronę w HelloAsso. Zarząd musi jeszcze utworzyć tam formularz darowizny: powyższe przyciski połączą się z nim automatycznie, bez zmian na stronie. Na razie prowadzą do strony stowarzyszenia.</p></div><h3 id=\"billetterie\">Bilety</h3><p>Rezerwacja online pozwala zająć miejsce z wyprzedzeniem, oszacować frekwencję i wysłać automatyczne przypomnienie dzień przed koncertem. Działa także przy wstępie wolnym: rezerwacja jest bezpłatna, a zbiórka odbywa się na miejscu.</p><h3 id=\"adhesion\">Członkostwo</h3><p>Składka wspiera bieżącą działalność stowarzyszenia i daje prawo głosu na dorocznym walnym zgromadzeniu.</p><h3 id=\"mecenat\">Mecenat firmowy</h3><p>Mecenat reguluje francuska ustawa Aillagon z 1 sierpnia 2003 roku: 60 % kwoty darowizny podlega odliczeniu od podatku dochodowego od osób prawnych, do 0,5 ‰ obrotu netto, z możliwością przeniesienia na pięć lat. W zamian firma otrzymuje widoczność (logo, wzmianka, zaproszenia) o wartości do 25 % kwoty darowizny.</p>",
"Ils nous soutiennent déjà": "Już nas wspierają",
"Nos partenaires": "Nasi partnerzy",
"<p class=\"lead\">Nous remercions chaleureusement nos sponsors pour leur soutien fidèle.</p>":
  "<p class=\"lead\">Serdecznie dziękujemy naszym sponsorom za niezmienne wsparcie.</p>",
"Une question sur le mécénat ?": "Pytanie o mecenat?",
"William Hege, président de l'association, répond directement aux entreprises et fondations qui souhaitent s'engager aux côtés de l'orchestre.":
  "William Hege, prezes stowarzyszenia, odpowiada bezpośrednio firmom i fundacjom, które chcą zaangażować się u boku orkiestry.",
"Prendre contact": "Nawiąż kontakt",
# ---------------------------------------------------------------- contact
"Contact — Orchestre de Chambre de Wissembourg": "Kontakt — Orchestre de Chambre de Wissembourg",
"Contacter l'Orchestre de Chambre de Wissembourg : projet de concert, candidature de musicien, mécénat, presse.":
  "Kontakt z Orkiestrą Kameralną Wissembourg: projekt koncertu, zgłoszenie muzyka, mecenat, prasa.",
"Écrivez-nous": "Napisz do nas",
"Un projet de concert, une question, une suggestion ? L'envie de rejoindre l'orchestre ? La volonté de devenir mécène ? Nous répondons à tous les messages.":
  "Projekt koncertu, pytanie, sugestia? Chęć dołączenia do orkiestry? Zamiar zostania mecenasem? Odpowiadamy na każdą wiadomość.",
"Coordonnées": "Dane kontaktowe",
"Orchestre de Chambre de Wissembourg": "Orchestre de Chambre de Wissembourg",
"E-mail": "E-mail",
"Adresse": "Adres",
"Président": "Prezes",
"Direction musicale": "Kierownictwo muzyczne",
"Trésorerie": "Skarbnik",
"Secrétariat": "Sekretariat",
"Réseaux": "Media społecznościowe",
"<a href=\"https://www.facebook.com/OrchestredeWissembourg/\" target=\"_blank\" rel=\"noopener\">Facebook — Orchestre de Wissembourg</a>":
  "<a href=\"https://www.facebook.com/OrchestredeWissembourg/\" target=\"_blank\" rel=\"noopener\">Facebook — Orchestre de Wissembourg</a>",
"Statut": "Status prawny",
"Nous écrire": "Napisz do nas",
"Une seule adresse pour toutes les demandes. Votre message arrive directement dans la boîte du bureau.":
  "Jeden adres do wszystkich spraw. Twoja wiadomość trafia wprost do skrzynki zarządu.",
"Pas de formulaire, pas de service tiers, aucune donnée enregistrée sur le site.":
  "Bez formularza, bez usług osób trzecich, żadnych danych zapisywanych na stronie.",
"Proposer un concert": "Zaproponuj koncert",
"Proposition de concert": "Propozycja koncertu",
"Candidature musicien": "Zgłoszenie muzyka",
"Mécénat et partenariat": "Mecenat i partnerstwo",
"Demande presse": "Zapytanie prasowe",
"Inscription à la lettre d'information": "Zapis do newslettera",
}

missing = []
def tr(o, path=""):
    if isinstance(o, dict):
        return {k: (v if k in SKIP_KEYS or k.startswith("_") else tr(v, f"{path}.{k}"))
                for k, v in o.items()}
    if isinstance(o, list):
        return [tr(v, f"{path}[{i}]") for i, v in enumerate(o)]
    if isinstance(o, str):
        if o in T:
            return T[o]
        if o.startswith("Saison 20"):          # « Saison 2013-2014 » → « Sezon 2013-2014 »
            return "Sezon " + o[7:]
        if o.startswith("mailto:") and "?subject=" in o:
            # L'objet pré-rempli est vu par l'utilisateur : il se traduit aussi.
            adr, sujet = o.split("?subject=", 1)
            if sujet in T:
                return f"{adr}?subject={T[sujet]}"
            missing.append((path + " [objet mailto]", sujet))
            return o
        if o.strip() and not o.startswith(("http", "page:", "media:", "ha:", "#", "mailto:")) and not o.isdigit():
            missing.append((path, o))
        return o
    return o

src = json.load(open("content/fr.json", encoding="utf-8"))
out = tr(copy.deepcopy(src))
out["lang"] = "pl"
out["locale"] = "pl_PL"
pathlib.Path("content/pl.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"pl.json écrit — {len(missing)} chaîne(s) non traduite(s)")
for p, s in missing:
    print(f"  {p} :: {s[:110]}")
