# -*- coding: utf-8 -*-
"""Dokument: El Niño 2026/2027 — jačina, putanja i posljedice."""

from docgen import BULLETS, H2, H3, P, SOURCES, TABLE, build

RUNNING = "Dokument — El Niño 2026/2027"

TITLE = "El Niño 2026/2027"
SUBTITLE = "Jačina događaja, putanja do proljeća 2027, globalne posljedice i račun koji za njim ide"

META = ("Predmet: razvoj i očekivani ishod El Niño događaja 2026/2027, sa težištem na mjerljivim "
        "veličinama i na posljedicama po hranu, ekonomiju i ekosisteme. Datum izrade: 20. avgust 2026. "
        "Stanje sistema opisano je zaključno sa dijagnostičkom raspravom NOAA CPC od 13. avgusta 2026. "
        "i pregledom IRI Columbia za avgust 2026. Uticaj na zimu nad Jadranom obrađen je u posebnom "
        "dokumentu o zimi 2026/2027. i ovdje se ne ponavlja. Prozor revizije: sredina novembra 2026, "
        "kada se očekuje vrhunac događaja.")

BLOCKS = [
    H2("Izvršni sažetak"),
    P("El Niño 2026/2027. je na putu da bude najjači zabilježen. Julska anomalija u regionu Niño 3.4 "
      "iznosila je +1,4 °C, u regionu Niño 1+2 čak +2,9 °C, a podpovršinske anomalije dosezale su "
      "+10 °C. NOAA daje preko 90 % izgleda za vrlo jak događaj tokom jeseni i zime i 69 % izgleda "
      "da tromjesečje oktobar–decembar pređe +2,5 °C po relativnom indeksu, čime bi nadmašilo sve "
      "događaje od 1950. godine. Od 26 modela u pregledu IRI, njih 15 daje vrhunac na +3,0 °C ili "
      "više, izvan najviše definisane kategorije jačine."),
    P("Tri stvari slijede iz toga skoro sigurno. Prva: 2027. će biti toplija od 2026. i najvjerovatnije "
      "najtoplija godina u istoriji mjerenja, jer globalna temperatura kasni za Pacifikom oko tri "
      "mjeseca. Druga: peto globalno izbjeljivanje koralnih grebena postaje vjerovatno, jer je svaki "
      "jak El Niño od 1998. bio praćen jednim. Treća: cijene hrane rastu sa zadrškom od dva do četiri "
      "tromjesečja, jer se gubitak prinosa u Australiji, Indoneziji i Indiji ne vidi odmah na "
      "berzama."),
    P("Ono što ne slijedi, a najčešće se tvrdi, jeste jednostavna posljedica po evropsko vrijeme. "
      "Veza tropskog Pacifika i Evrope je posredna, prolazi kroz stratosferu i mijenja se od decenije "
      "do decenije. Sve konkretno što se o tome može reći za naše krajeve stoji u odvojenom dokumentu "
      "o zimi 2026/2027."),
    P("Račun na kraju ne stiže onima koji su ga napravili. Zemlje sa najjačom vezom prema El Niñu su "
      "tropske zemlje niskog i srednjeg dohotka — Ekvador, Peru, Indonezija, Malezija — i njihov "
      "gubitak se mjeri u procentima domaćeg proizvoda, a ne u promilima."),

    H2("Mehanizam i mjerne veličine"),
    P("U normalnim godinama pasati guraju toplu površinsku vodu ka zapadnom Pacifiku, gdje se gomila "
      "u toplotni bazen, dok se uz obalu Južne Amerike diže hladna voda iz dubine. U El Niñu pasati "
      "slabe ili se u epizodama okreću, topla voda se u vidu Kelvinovog talasa vraća na istok, "
      "termoklina uz Južnu Ameriku tone i uzdizanje hladne vode prestaje. Kiša ide za toplom vodom, "
      "pa se tropski pojas oborina pomjera hiljadama kilometara na istok, a s njim i položaj mlaznih "
      "struja koje raspoređuju vrijeme na obje hemisfere."),
    P("Jačina se prati preko nekoliko veličina. ONI je tromjesečni prośek anomalije temperature mora u "
      "regionu Niño 3.4, sa referentnom osnovom koja se pomjera svakih pet godina. RONI je isti "
      "indeks umanjen za prośečno zagrijavanje cijelog tropskog pojasa i zato pošteno poredi događaje "
      "kroz decenije: u zagrijanom okeanu današnji ONI precjenjuje atmosferski odgovor, jer atmosfera "
      "reaguje na razliku u odnosu na okolinu, a ne na apsolutnu temperaturu. Uz njih se prate "
      "indeksi južne oscilacije, koji mjere razliku pritiska između Tahitija i Darvina, i toplotni "
      "sadržaj gornjih 300 m okeana, koji daje najranije upozorenje."),

    H2("Stanje u avgustu 2026"),
    TABLE("Tabela 1. Stanje ENSO sistema i projekcija, prema dijagnostičkoj raspravi NOAA CPC od "
          "13. avgusta 2026, pregledu IRI Columbia za avgust 2026. i biltenu australijskog biroa od "
          "11. avgusta 2026. Sedmične vrijednosti indeksa razlikuju se između proizvoda zbog "
          "različite referentne osnove i različite obrade satelitskih podataka.",
          ["Veličina", "Vrijednost", "Značenje"],
          [["Niño 3.4, jul 2026", "+1,4 °C", "prag za jak događaj je +1,5 °C, prag za vrlo jak +2,0 °C"],
           ["Niño 3, jul 2026", "+1,7 °C", "težište zagrijavanja u istočnom Pacifiku"],
           ["Niño 1+2, jul 2026", "+2,9 °C", "uz obalu Perua i Ekvadora, tip događaja kao 1982. i 1997."],
           ["Podpovršinska anomalija", "do +10 °C", "rezervoar toplote koji tek izlazi na površinu"],
           ["Indeksi južne oscilacije", "oko −2 standardne devijacije", "atmosfera je već u punom odgovoru"],
           ["Sedmični Niño 3.4, sredina avgusta", "+2,2 do +2,7 °C zavisno od proizvoda",
            "događaj je već u kategoriji vrlo jakog"],
           ["RONI, medijana okt–dec 2026", "+2,66 °C", "sredina raspodjele +2,37 do +2,95 °C"],
           ["RONI, medijana dec–feb 2026/27", "+2,23 °C", "vrhunac u kasnu jesen, zatim polagano opadanje"],
           ["Izgledi za rekordan događaj (≥ +2,5 °C, okt–dec)", "69 %", "jače od svega od 1950. godine"],
           ["Modeli sa vrhuncem ≥ +3,0 °C", "15 od 26", "izvan najviše definisane kategorije IRI"],
           ["Vjerovatnoća trajanja kroz feb–apr 2027", "100 %", "raspad tek u proljeće 2027."],
           ["Indeks dipola Indijskog okeana, 9.8.2026", "+0,41 °C", "pozitivna faza pojačava tropsko forsiranje"]],
          widths=[34, 30, 36]),
    P("Uz El Niño se razvija i pozitivan dipol u Indijskom okeanu, sa indeksom koji je 9. avgusta "
      "treću sedmicu zaredom bio iznad praga. Kombinacija ta dva obrasca istorijski daje suvlje i "
      "toplije uslove nad Australijom i jugoistočnom Azijom nego bilo koji od njih zasebno, i "
      "pojačava odgovor cirkulacije śeverne hemisfere."),

    H2("Koliko je jak u poređenju sa prethodnim događajima"),
    TABLE("Tabela 2. Vrhunci indeksa ONI kod najjačih zabilježenih događaja, prema NOAA CPC. Podatak "
          "za 2026/27. je projekcija, a ne izmjerena vrijednost, i dat je preko relativnog indeksa "
          "RONI zato što se preko njega jedino i može porediti sa događajima iz prošlog vijeka.",
          ["Događaj", "Vrhunac ONI", "Zapamćeno po"],
          [["1972/73", "+2,1 °C", "kolaps ribolova inćuna u Peruu"],
           ["1982/83", "+2,2 °C", "poplave u Ekvadoru i Peruu, suša i požari u Australiji"],
           ["1997/98", "+2,4 °C", "prvo globalno izbjeljivanje koralnih grebena, rekordno topla 1998."],
           ["2015/16", "+2,6 °C", "najjači u nizu od 1950; suša u Etiopiji, rekordno topla 2016."],
           ["2026/27", "projekcija ≥ +2,5 °C (RONI)", "69 % izgleda da nadmaši sve prethodne"]],
          widths=[16, 24, 60]),
    P("Poređenje traži jedan oprez. Apsolutne temperature mora danas su više nego 1997. ili 2015. "
      "godine za oko pola stepena, zbog opšteg zagrijavanja okeana, pa svaki novi događaj lakše "
      "obori apsolutni rekord nego što obori rekord u atmosferskom odgovoru. Zato NOAA i naglašava "
      "relativni indeks. Ono što ostaje nesporno jeste da je toplotni sadržaj koji je u avgustu 2026. "
      "bio uskladišten ispod površine među najvećima ikad izmjerenim, i da taj rezervoar tek treba da "
      "se isprazni u atmosferu."),

    H2("Putanja do proljeća 2027. i nesigurnost"),
    P("Vrhunac se očekuje između novembra 2026. i januara 2027, što je tipično: El Niño se "
      "sinhronizuje sa godišnjim ciklusom i skoro uvijek kulminira oko zimskog solsticija śeverne "
      "hemisfere. Raspad počinje u proljeće, a IRI daje 97 % vjerovatnoće za nastavak događaja u "
      "mart–maj 2027. i 78 % u april–jun 2027. Poslije jakog događaja često, ali ne uvijek, slijedi "
      "La Niña: tako je bilo 1983, 1998. i 2016. godine."),
    P("Glavna nesigurnost nije da li će događaj biti jak, nego koliko će atmosfera na njega odgovoriti "
      "i koliko će brzo popustiti. Modeli od maja do jula griješe najviše — proljećna prognostička "
      "barijera — ali avgustovske inicijalizacije su znatno pouzdanije, pa je današnja slika stabilnija "
      "od onoga što se moglo reći u maju. Druga nesigurnost je odnos sa dipolom Indijskog okeana, koji "
      "se obično raspada u decembru; ako se raspadne ranije, dio suvog signala nad Australijom slabi "
      "prije sezone požara."),

    H2("Globalna temperatura 2026. i 2027."),
    P("Globalna temperatura kasni za Pacifikom oko tri mjeseca, pa se najveći dio ovog događaja neće "
      "vidjeti u 2026. nego u 2027. godini. Jul 2026. bio je zajedno drugi najtopliji jul u zapisu, sa "
      "16,90 °C i 1,47 °C iznad predindustrijskog nivoa, a vanpolarni okean imao je najtopliji jul "
      "ikad, 20,96 °C. Carbon Brief daje za 2027. centralnu procjenu od oko 1,71 °C iznad "
      "predindustrijskog nivoa, sa 90-postotnim rasponom 1,49 do 1,93 °C, što bi bio ubjedljiv novi "
      "rekord. WMO u petogodišnjoj najavi za period 2026–2030. daje 91 % izgleda da bar jedna godina "
      "privremeno pređe 1,5 °C, 75 % da to učini i petogodišnji prośek, i 86 % da bar jedna godina "
      "nadmaši rekordnu 2024."),
    P("Prekoračenje od jedne godine nije isto što i probijanje Pariskog cilja, koji se odnosi na "
      "dugoročni prośek. Razlika je stvarna, ali se smanjuje: petogodišnji prośek koji sa tri "
      "četvrtine vjerovatnoće prelazi 1,5 °C znači da se razgovor pomjera sa toga hoće li se granica "
      "preći na to koliko će je se preći."),

    H2("Regionalne posljedice"),
    TABLE("Tabela 3. Očekivane regionalne posljedice događaja 2026/2027, prema analizi Zajedničkog "
          "istraživačkog centra Evropske komisije iz juna 2026, pregledu World Resources Institute i "
          "sezonskim najavama nacionalnih službi. Raspored je tipičan za jak El Niño; jačina odgovora "
          "varira od događaja do događaja.",
          ["Područje", "Očekivano", "Sektor pod udarom"],
          [["Australija (istok i jug)", "toplije i suvlje; proljećna temperatura oko 2 °C iznad osnove 1961–1990",
            "pšenica, stočarstvo, sezona požara"],
           ["Indonezija, Malezija, Filipini", "toplije i suvlje, prazne akumulacije",
            "pirinač, palmino ulje, kafa, hidroelektrane"],
           ["Indija i Šri Lanka", "slabiji monsun, deficit u centralnom i śevernom dijelu",
            "pirinač, šećer, cijene osnovnih namirnica"],
           ["Južna Afrika i Sahel", "suša u južnom dijelu kontinenta", "kukuruz, stočarstvo, snabdijevanje vodom"],
           ["Istočna Afrika", "obilne padavine i poplave", "raseljavanja, kolera, saobraćaj"],
           ["Zapadna obala Južne Amerike", "obilne padavine u Peruu i Ekvadoru; kraj uzdizanja hladne vode",
            "poplave, klizišta, ribolov inćuna"],
           ["Amazonija", "suša i požari; u 2015/16. i 2023/24. izgorjelo preko 2,3 miliona ha godišnje, "
            "četiri puta iznad prośeka 2001–2025", "šume, kvalitet vazduha, plovnost rijeka"],
           ["Śeverna Amerika", "vlažniji jug SAD-a, blaži śever", "poplave u Kaliforniji, niža potrošnja za grijanje"],
           ["Atlantik", "pojačano smicanje vjetra guši razvoj uragana; NOAA je 6. avgusta 2026. spustila "
            "prognozu na 7–13 imenovanih oluja i podigla izglede za ispodprośečnu sezonu sa 55 na 75 %",
            "osiguranje, obalna infrastruktura"],
           ["Koralni grebeni", "NOAA Coral Reef Watch 21. jula 2026. daje visok rizik od izbjeljivanja "
            "od avgusta do novembra", "ribarstvo, turizam, zaštita obale"]],
          widths=[24, 46, 30]),

    H2("Hrana i tržišta"),
    P("Udar na hranu ne dolazi odjednom nego u talasima, jer se sjetve i žetve na juž"
      "noj i śevernoj hemisferi ne poklapaju. Prvi talas ide preko australijske pšenice i "
      "jugoistočnoazijskog pirinča i palminog ulja u sezoni 2026/27, drugi preko indijskog pirinča i "
      "šećera, treći preko južnoameričke soje i kafe. Analiza Zajedničkog istraživačkog centra iz juna "
      "2026. očekuje oštar rast cijene durum pšenice, blag rast kukuruza, pad soje i tvrde crvene "
      "zimske pšenice, i za pirinač prvo pad pa rast u kasnijoj fazi."),
    P("Glavni ekonomista Organizacije za hranu i poljoprivredu izdvojio je durum pšenicu i pirinač kao "
      "najosjetljivije, zbog spoja El Niña sa smanjenom upotrebom vještačkog đubriva. Pojedine "
      "industrijske analize pominju rast globalne inflacije cijena hrane do 9 %, ali te brojke treba "
      "čitati kao gornji scenario zainteresovane strane, ne kao prognozu. Ono što je u istoriji "
      "dosljedno jeste da rast svjetskih cijena osnovnih namirnica najbrže pogađa domaćinstva koja "
      "žive od dnevne nadnice, jer je hrana jedina stavka njihovog budžeta koja se ne može odložiti."),

    H2("Ekonomski račun"),
    P("Callahan i Mankin (2023, Science) pokazali su da se ekonomski trag El Niña ne zaustavlja na "
      "godini događaja: rast ostaje potisnut najmanje pet godina, a u nekim slučajevima i duže od "
      "decenije. Njihova procjena globalnog gubitka dohotka pripisanog događaju 1982/83. iznosi 4,1 "
      "bilion dolara, a događaju 1997/98. čak 5,7 biliona. Za dvadeset prvi vijek, uz pojačanje "
      "događaja klimatskim promjenama, projektuju kumulativni gubitak od 84 biliona dolara."),
    P("Primjena istih elastičnosti na događaj 2026/27, koju je u 2026. objavio Peterson Institute for "
      "International Economics, daje gubitak prve godine od oko 990 milijardi dolara, blizu 0,8 % "
      "svjetskog proizvoda, i šestogodišnji kumulativ u vrlo širokom rasponu od 7 do 28 biliona. "
      "Raspon je toliko širok jer se množi pretpostavkama o trajanju potisnutog rasta; korisniji je "
      "podatak da za 51 zemlju sa jakom vezom prema Pacifiku, čiji zajednički proizvod iznosi 9,9 "
      "biliona dolara, gubitak dostiže 3,6 % njihovog proizvoda."),
    P("Prevedeno: događaj koji u razvijenim zemljama izgleda kao statistička nijansa, u Ekvadoru, "
      "Peruu, Indoneziji ili Maleziji izgleda kao izgubljena godina rasta."),

    H2("Humanitarne posljedice"),
    P("Zajednički istraživački centar je u junu 2026. objavio analizu koja spaja sezonske najave sa "
      "podacima o ranjivosti stanovništva. Najviši rizik nose Centralna Afrika, Sudan, Somalija, Južni "
      "Sudan, Čad, Ekvador, Venecuela i Haiti — zemlje u kojima se klimatski šok slaže na sukob, "
      "raseljenost ili slabu državu. Vrhunac toplotnog opterećenja u tropima i suptropima očekuje se "
      "od decembra 2026. do februara 2027, sa nastavkom u proljeće."),
    P("Procjene broja ljudi koji bi zbog ovog događaja ušli u akutnu nesigurnost u ishrani do kraja "
      "2027. kreću se oko 50 miliona. Takve brojke su po prirodi neizvjesne i zavise od toga koliko će "
      "se rano djelovati. Za razliku od zemljotresa, El Niño je najavljen mjesecima unaprijed, pa "
      "svaki propušteni mjesec priprema jeste odluka, a ne nesreća."),

    H2("Ekosistemi"),
    P("Koralni grebeni su najosjetljiviji pokazatelj. Od januara 2023. do septembra 2025. toplotni "
      "stres dovoljan za izbjeljivanje pogodio je oko 84 % površine svjetskih grebena u okviru "
      "četvrtog globalnog događaja izbjeljivanja. Prognoza NOAA Coral Reef Watch od 21. jula 2026. "
      "daje visok rizik od izbjeljivanja od avgusta do novembra, sa težištem na śevernom Pacifiku, "
      "Havajima, Floridi i Karibima. Peti globalni događaj bio bi peti otkad se prati, a prvi je bio "
      "1998, poslije istog ovakvog El Niña."),
    P("Uz grebene ide i ribarstvo. Prestanak uzdizanja hladne vode uz Peru raseljava i prorjeđuje "
      "inćuna, čime se pogađa najveći svjetski ribolov i lanac hrane za akvakulturu i stočarstvo "
      "širom svijeta. Taj efekat je bio vidljiv u svakom jakom događaju od 1972. naovamo."),

    H2("Šta ovo znači za Crnu Goru"),
    P("Ne mnogo direktno, i to je poštena rečenica koju sezonske najave rijetko izgovore. Uticaj na "
      "vrijeme nad Jadranom ide preko stratosfere i Śevernog Atlantika, slab je i neuredan, i "
      "razrađen je u dokumentu o zimi 2026/2027. Indirektni uticaji su izvjesniji od direktnih:"),
    BULLETS([
        "cijene hrane, naročito uvoznih žitarica, ulja i kafe, sa zadrškom od dva do četiri "
        "tromjesečja;",
        "topla 2027. godina, koja će u ljetnjoj sezoni značiti još jedno ljeto na gornjem kraju "
        "raspodjele, sa svime što ide uz njega — požari, potrošnja vode, toplotni stres;",
        "more koje ni u jesen 2027. neće imati priliku da se ohladi na nekadašnje vrijednosti, jer "
        "toplotni sadržaj Sredozemlja ne prati godišnji ciklus Pacifika;",
        "turizam, kroz cijene avio-goriva i kroz percepciju juga Evrope kao pretople destinacije u "
        "julu i avgustu.",
    ]),

    H2("Šta bi promijenilo ovu sliku"),
    P("Tri stvari. Prvo, brz prestanak zapadnih anomalija vjetra u ekvatorijalnom Pacifiku tokom "
      "septembra, koji bi zaustavio dalje jačanje i zadržao vrhunac oko +2,0 °C umjesto preko +2,5 °C. "
      "Drugo, raniji raspad dipola u Indijskom okeanu, koji bi ublažio suvi signal nad Australijom i "
      "jugoistočnom Azijom, a time i najveći dio poljoprivrednog udara. Treće, brz raspad događaja u "
      "januaru umjesto u proljeće, koji bi smanjio zaostali efekat na globalnu temperaturu u 2027. i "
      "na cijene u 2028."),
    P("Naredni kontrolni datumi su 10. septembar i 8. oktobar 2026, kada izlaze dijagnostičke rasprave "
      "NOAA, i sredina novembra, kada se očekuje sam vrhunac."),

    H2("Zaključak"),
    P("Ovo je događaj koji će se pamtiti po broju: preko 90 % izgleda za vrlo jak El Niño, 69 % "
      "izgleda da bude najjači od 1950. godine, 15 od 26 modela iznad +3,0 °C. Za većinu svijeta on "
      "neće izgledati kao jedan događaj nego kao niz naizgled nepovezanih nevolja — suša u Australiji, "
      "poplave u Keniji, izbijeljeni grebeni na Havajima, skuplji pirinač u Manili, najtoplija godina "
      "u istoriji mjerenja u 2027."),
    P("Za Crnu Goru posljedice će stići posredno i sporo. Viđeće se kao skuplja hrana, kao još jedno "
      "vrlo toplo ljeto i kao more koje u novembru ostaje toplije nego što bi trebalo."),

    H2("Izvori"),
    SOURCES([
        "NOAA Climate Prediction Center, ENSO Diagnostic Discussion, 13. avgust 2026.",
        "IRI Columbia, ENSO Quick Look i model plume, avgust 2026.",
        "Bureau of Meteorology (Australija), Climate Driver Update, 11. avgust 2026.",
        "NOAA, ažurirana najava sezone uragana u Atlantiku, 6. avgust 2026.",
        "NOAA Coral Reef Watch, četvoromjesečna prognoza izbjeljivanja, 21. jul 2026.",
        "Zajednički istraživački centar Evropske komisije, analiza humanitarnih posljedica "
        "El Niña, 15. jun 2026.",
        "World Resources Institute, pregled posljedica super El Niña, 2026.",
        "Copernicus Climate Change Service, bilten o površinskoj temperaturi za jul 2026.",
        "Carbon Brief, procjena globalne temperature za 2026. i 2027. godinu.",
        "WMO, Global Annual to Decadal Climate Update 2026–2030.",
        "Callahan, C. W. i Mankin, J. S. (2023), Persistent effect of El Niño on global economic "
        "growth, Science 380, 1064–1070.",
        "Peterson Institute for International Economics, procjena ekonomskih gubitaka od El Niña, 2026.",
    ]),
]


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "20_VIII_MMXXVI_el_nino.pdf")
    build(out, RUNNING, TITLE, SUBTITLE, META, BLOCKS)
    print(out)
