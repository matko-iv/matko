# -*- coding: utf-8 -*-
"""Dokument: klimatske promjene i Balkan do 2030."""

from docgen import BULLETS, H2, H3, P, SOURCES, TABLE, build

RUNNING = "Dokument — klimatske promjene i Balkan do 2030"

TITLE = "Balkan do 2030"
SUBTITLE = ("Šta je već izmjereno, šta je za narednih pet godina praktično zaključano i gdje će se "
            "to najprije osjetiti")

META = ("Predmet: uticaj klimatskih promjena na Balkan, sa težištem na zapadnom Balkanu i "
        "crnogorskom primorju, na horizontu do 2030. godine. Datum izrade: 20. avgust 2026. "
        "Izmjerene vrijednosti računate su iz ERA5 reanalize za tačke Budve i Podgorice, period "
        "1950–2026, i dopunjene izvještajima službe Copernicus, Zajedničkog istraživačkog centra "
        "Evropske komisije, WMO, MedECC i Svjetske banke. Horizont 2030. izabran je namjerno: to je "
        "period u kojem su scenariji emisija još uvijek gotovo nerazlučivi, pa je ono što slijedi "
        "bliže prognozi nego izboru.")

BLOCKS = [
    H2("Izvršni sažetak"),
    P("Do 2030. godine Balkan neće dobiti novu klimu. Dobiće pojačanu verziju one koja se već "
      "izmjerila u posljednjih petnaest godina, i to sa oko pola stepena dodatnog zagrijavanja u "
      "odnosu na današnji prośek. Sve ostalo je već u sistemu. Zbog inercije okeana i zbog toga što se "
      "putanje emisija razilaze tek poslije 2040, razlika između najambicioznijeg i najgoreg scenarija "
      "za 2030. iznosi manje od dvije desetine stepena. To ne znači da je svejedno šta se radi; znači "
      "da je za narednih pet godina prilagođavanje važnije od smanjenja emisija."),
    P("Mjerljivo stanje: Evropa se zagrijava po 0,56 °C na deceniju, dvostruko brže od globalnog "
      "prośeka od 0,27 °C. Sredozemno more se zagrijava po 0,41 °C na deceniju i u julu 2026. imalo je "
      "najtopliju površinu u zapisu, 27,07 °C. Na tački Budve, broj dana sa maksimumom iznad 30 °C "
      "porastao je sa 13 godišnje u periodu 1961–1990. na 44 u periodu 2011–2025. Na tački Podgorice, "
      "broj dana iznad 35 °C porastao je sa 1 na 18 između ista dva perioda."),
    P("Do 2030. najizvjesnije posljedice su: produžena ljetnja sezona toplotnog stresa od maja do "
      "oktobra, češće i duže suše u zaleđu uz istovremeno intenzivnije pojedinačne padavine, "
      "smanjena i nesigurnija proizvodnja u hidroelektranama, požarne sezone poput ove iz 2026. kao "
      "redovna a ne izuzetna pojava, i turistička sezona koja se rasteže u proljeće i jesen dok jul i "
      "avgust gube na udobnosti."),
    P("Najveći jaz nije u nauci nego u pripremi. Crna Gora nema usvojen plan prilagođavanja, mreža "
      "vodosnabdijevanja na primorju gubi između 30 i 45 % vode, a sistemi za odvođenje kišnice "
      "građeni su za raspodjelu padavina koja više ne postoji. Ti nedostaci se ne mjere u stepenima "
      "nego u milionima eura po epizodi."),

    H2("Zašto baš 2030"),
    P("Klimatski scenariji se u javnosti obično predstavljaju za 2100. godinu, gdje je razlika između "
      "putanja dramatična i gdje se ništa ne može provjeriti. Horizont 2030. radi suprotno. Zbog "
      "toplotne inercije okeana i zbog aerosola koji su već u atmosferi, temperatura naredne "
      "decenije praktično je određena onim što je već emitovano. WMO u petogodišnjoj najavi za "
      "period 2026–2030. daje 91 % izgleda da bar jedna godina privremeno pređe 1,5 °C iznad "
      "predindustrijskog nivoa, 75 % da to učini i petogodišnji prośek, i 86 % da bar jedna godina "
      "nadmaši rekordnu 2024. Raspon godišnjih vrijednosti je 1,3 do 1,9 °C."),
    P("Za planiranje to znači da se pitanje pomjera. Ne pita se više šta će biti ako se klima "
      "promijeni, nego koliko brzo se infrastruktura, poljoprivreda i turizam mogu prilagoditi klimi "
      "koja je već ovdje. Investicioni ciklus vodovoda, puta ili hotela traje trideset godina; klima "
      "za koju su građeni prestala je da postoji prije petnaest."),

    H2("Šta je već izmjereno"),
    H3("Kontinent i more"),
    P("Copernicus je u izvještaju o stanju evropske klime za 2025. godinu, objavljenom 29. aprila "
      "2026, utvrdio da se Evropa u posljednjih trideset godina zagrijava po 0,56 °C na deceniju, "
      "dvostruko brže od globalnog prośeka od 0,27 °C, i da je najbrže zagrijavajući kontinent. "
      "Najmanje 95 % Evrope imalo je 2025. godišnju temperaturu iznad prośeka. Prośečna godišnja "
      "temperatura površine mora oko Evrope bila je najviša u zapisu četvrtu godinu zaredom, a 86 % "
      "evropskih mora bilo je pod bar „jakim” morskim toplotnim talasom."),
    P("Sredozemno more se zagrijava po 0,41 °C na deceniju, dvostruko brže od svjetskog okeana. Jadran "
      "je među najbržim podregionima. Jul 2026. bio je najtopliji jul u zapisu Sredozemlja, sa 27,07 ± "
      "0,27 °C, iznad rekorda iz 2025. od 26,68 ± 0,11 °C. Uz južnu obalu Hrvatske more je sredinom "
      "avgusta 2026. mjerilo 28 °C; hrvatski rekord od 29,7 °C postavljen je u Dubrovniku 2024."),
    H3("Crna Gora, mjereno na dvije tačke"),
    P("Za lokalni prikaz korištena je ERA5 reanaliza za tačke Budve (42,28° SGŠ, 18,84° IGD) i "
      "Podgorice (42,44° SGŠ, 19,26° IGD). ERA5 je mreža od oko 9 km i miješa more, dolinu i planinu, "
      "pa su apsolutne vrijednosti pomjerene u odnosu na stanicu — za Podgoricu naročito, jer mreža "
      "uvlači okolne planine i time potcjenjuje broj vrelih dana. Trendovi i odnosi između perioda "
      "ostaju valjani, jer ista pristrasnost pogađa sve periode jednako."),
    TABLE("Tabela 1. Izmjerene promjene na tačkama Budve i Podgorice, ERA5, poređenje standardnih "
          "tridesetogodišnjih perioda i posljednjih petnaest godina. Tropska noć je noć sa minimumom "
          "od 20 °C ili više. Vrijednosti za 2026. odnose se na period do 18. avgusta i nijesu "
          "konačne.",
          ["Pokazatelj", "1961–1990", "1991–2020", "2011–2025", "2026 (do 18.8)"],
          [["Budva, godišnja srednja temperatura", "15,8 °C", "16,5 °C", "17,2 °C", "—"],
           ["Budva, dani sa Tmax ≥ 30 °C", "13", "31", "44", "—"],
           ["Budva, tropske noći", "63", "81", "92", "69"],
           ["Budva, godišnje padavine", "2223 mm", "2108 mm", "2245 mm", "—"],
           ["Podgorica, godišnja srednja temperatura", "13,6 °C", "14,8 °C", "15,7 °C", "—"],
           ["Podgorica, dani sa Tmax ≥ 30 °C", "18", "43", "67", "—"],
           ["Podgorica, dani sa Tmax ≥ 35 °C", "1", "6", "18", "29"],
           ["Podgorica, godišnje padavine", "2037 mm", "1901 mm", "1824 mm", "—"]],
          widths=[38, 15, 15, 16, 16]),
    P("Iz tabele izlaze četiri nalaza. Prvo, zagrijavanje je brže u unutrašnjosti nego na obali: trend "
      "godišnje temperature iznosi +0,33 °C po deceniji na tački Podgorice prema +0,21 °C na tački "
      "Budve. Drugo, ljeto se zagrijava brže od godišnjeg prośeka — ljetni trend je +0,47 °C po "
      "deceniji u Podgorici i +0,33 °C u Budvi. Treće, promjena se ne vidi toliko u srednjoj "
      "vrijednosti koliko u broju ekstremnih dana: broj dana iznad 30 °C u Podgorici se od "
      "šezdesetih godina skoro učetvorostručio. Četvrto, padavine na obali nemaju jasan trend, dok "
      "unutrašnjost gubi oko 10 % u odnosu na period 1961–1990."),
    P("Ljeto 2026. je na tački Budve, računato od 1. juna do 18. avgusta, najtoplije u nizu od 1950. "
      "godine, sa 27,63 °C prema 27,57 °C iz 2024. i klimatološkom vrijednošću od 25,18 °C. Razlika u "
      "odnosu na drugoplasiranu godinu je unutar granice greške, pa je poštenije reći da su 2026. i "
      "2024. na istom mjestu, skoro pola stepena iznad svega ostalog u nizu."),
    H3("Ljeto 2026. kao ilustracija"),
    P("Sezona 2026. je pokazala kako izgleda spoj toplote i suše u praksi. Sredinom avgusta 50 % "
      "teritorije Evropske unije i Ujedinjenog Kraljevstva bilo je u nekoj kategoriji suše, sa 9 % u "
      "kategoriji „alarm”. Loara, Po, Rajna i Dunav dostigli su rekordno niske vodostaje; Dunav se "
      "spustio do granice plovnosti, pa je rafinerija u Pančevu 4. avgusta prepolovila preradu. Mostar "
      "je 30. jula imao 42 °C. Do 5. avgusta u Evropi je izgorjelo 505 683 ha, prema 379 392 ha do "
      "istog datuma 2025, a Crna Gora je po udjelu izgorjele u ukupnoj teritoriji prošla gore od "
      "Španije i Portugala. Procjene viška smrtnih slučajeva usljed toplote kreću se od preko 10 000 "
      "u pet zemalja, prema Svjetskoj zdravstvenoj organizaciji, do oko 25 000 na nivou kontinenta u "
      "novinarskim proračunima."),

    H2("Šta modeli daju do 2030"),
    P("Projekcije za Crnu Goru, izrađene za nacionalne izvještaje prema Okvirnoj konvenciji UN, daju "
      "za period 2011–2040. po scenariju RCP8.5 odstupanje srednje godišnje temperature od +1,5 do "
      "+2 °C u odnosu na referentni period 1971–2000. Padavine se do 2040. mijenjaju suprotno po "
      "regionima: do +5 % godišnje u śevernom planinskom dijelu, do −5 % na jugu. Uz to se mijenja i "
      "priroda padavina — manje snijega, više kiše, i veći udio godišnjeg zbira koji padne u malom "
      "broju obilnih epizoda."),
    P("Za širi mediteranski okvir, MedECC daje da region već sada ima godišnju temperaturu 1,4 °C "
      "iznad perioda 1880–1899, da se prośečne padavine smanjuju za oko 4 % po stepenu globalnog "
      "zagrijavanja, i da bi na 2 °C globalnog zagrijavanja toplotni ekstremi u Sredozemlju porasli za "
      "oko 3 °C, a učestalost poljoprivrednih suša za 150 do 200 %. Prośečni porast nivoa mora za "
      "bazen Sredozemlja procijenjen je na 9,8 do 25,6 cm do perioda 2040–2050, zavisno od scenarija."),
    TABLE("Tabela 2. Sažetak projekcija za horizont do 2030, sa naznakom pouzdanosti. Pouzdanost se "
          "odnosi na smjer i red veličine, ne na tačnu brojku. Tamo gdje se izvori razlikuju, dat je "
          "raspon.",
          ["Veličina", "Do 2030", "Pouzdanost"],
          [["Globalna temperatura (godišnje)", "1,3 do 1,9 °C iznad predindustrijskog nivoa; 91 % "
            "izgleda za bar jednu godinu preko 1,5 °C", "visoka"],
           ["Godišnja temperatura na zapadnom Balkanu",
            "+0,3 do +0,6 °C u odnosu na prośek 2011–2025", "visoka"],
           ["Ljetnja temperatura", "raste brže od godišnje, oko +0,5 °C po deceniji u unutrašnjosti",
            "visoka"],
           ["Godišnje padavine", "bez jasne promjene na obali; blagi pad u unutrašnjosti i na jugu",
            "niska"],
           ["Intenzitet pojedinačnih padavinskih epizoda", "raste, oko 7 % više vlage po stepenu",
            "srednja do visoka"],
           ["Ljetnja suša (SPEI)", "češća i duža, prije svega zbog isparavanja a ne zbog manje kiše",
            "srednja do visoka"],
           ["Temperatura Jadrana", "+0,2 do +0,3 °C u odnosu na današnji prośek; morski toplotni "
            "talasi skoro svake godine", "visoka"],
           ["Nivo mora na crnogorskoj obali", "oko 3 do 5 cm u odnosu na danas", "srednja"],
           ["Snježni pokrivač ispod 1400 m", "kraće trajanje, kasniji početak sezone", "visoka"],
           ["Požarna sezona", "duža za dvije do četiri nedjelje u odnosu na kraj 20. vijeka",
            "srednja do visoka"]],
          widths=[30, 50, 20]),

    H2("Sektori"),
    H3("Voda"),
    P("Voda je najosjetljivija tačka regiona i prva na kojoj se promjena vidi. Problem nije toliko "
      "ukupna količina padavina, koja se do 2030. neće dramatično promijeniti, koliko njihov "
      "raspored i pojačano isparavanje. Ljeto sa temperaturom višom za dva stepena troši više vode iz "
      "tla i akumulacija čak i kad padne ista kiša, pa indeks SPEI, koji uključuje isparavanje, "
      "pokazuje sušenje i tamo gdje indeks SPI ne pokazuje ništa."),
    P("Praktične posljedice su već zabilježene. U ljeto 2025. zemlje zapadnog Balkana uvodile su "
      "ograničenja u snabdijevanju vodom, a Srbija je proglasila „ekstremnu sušu” i uvela restrikcije "
      "u manjim mjestima. Skadarsko jezero ima statistički značajan trend pada nivoa u kasnom ljetu, "
      "što direktno pogađa izvorišta koja snabdijevaju primorje. Krš, koji čini veći dio Crne Gore, "
      "vodu brzo propušta i teško zadržava, pa je sistem po prirodi osjetljiv na višenedjeljni "
      "izostanak kiše."),
    P("Uz to ide i gubitak u mreži. U vodovodnom sistemu crnogorskog primorja gubici se procjenjuju "
      "na 30 do 45 %, što znači da se između trećine i skoro polovine zahvaćene vode ne isporuči "
      "korisniku. Ni jedna klimatska projekcija ne mijenja činjenicu da je to najjeftinija dostupna "
      "rezerva vode u regionu."),
    H3("Energetika"),
    P("Zapadni Balkan pokriva veliki dio potrošnje električne energije iz hidroelektrana, što ga čini "
      "neuobičajeno osjetljivim na sušu. U sušnoj godini proizvodnja pada upravo onda kada potrošnja "
      "za hlađenje raste, pa se deficit rješava uvozom po najvišim ljetnjim cijenama. Albanija je u "
      "prvoj polovini 2025. na uvoz struje potrošila oko 60 miliona eura zbog niskog nivoa akumulacija. "
      "Procjene za albanske hidroelektrane govore o mogućem padu godišnje proizvodnje od 15 % u velikim "
      "i 20 % u malim postrojenjima, a za region se pominje pad od 20 % i više u nepovoljnim godinama."),
    P("Sa druge strane raste potrošnja za hlađenje. Broj tropskih noći na crnogorskom primorju već je "
      "prešao 90 godišnje, a svaka tropska noć znači klima-uređaje koji rade cijelu noć. Do 2030. "
      "ljetnji vršni teret postaje ozbiljniji problem od zimskog, što je obrnuto od pretpostavke na "
      "kojoj je mreža projektovana."),
    H3("Poljoprivreda"),
    P("Sezona 2026. je pokazala mehanizam. Suša i toplota u junu i julu pogodile su kukuruz u fazi "
      "oprašivanja, što je najosjetljiviji trenutak u ciklusu; procjene prinosa za kukuruz i suncokret "
      "na nivou Evropske unije snižene su za 6 do 7 %. U śeveroistočnoj Bosni nestali su usjevi "
      "djeteline koji su ranije bili pouzdani. Za Crnu Goru najizloženiji su Zeta i Crmnica, sa "
      "povrćem, vinogradima i maslinjacima koji zavise od navodnjavanja."),
    P("Do 2030. glavni rizik nije prośečno smanjenje prinosa nego rast varijabilnosti: naizmjenične "
      "godine sa dobrim i sa katastrofalnim prinosom teže su za mala gazdinstva od dosljednog blagog "
      "pada. Uz to raste rizik od kasnog proljećnog mraza, jer se vegetacija budi ranije, i pritisak "
      "štetočina koje u blagim zimama prezimljavaju u većem broju."),
    H3("Šume i požari"),
    P("Požarna sezona 2026. je bila jedna od najgorih u evropskom zapisu, a Crna Gora je po udjelu "
      "izgorjele površine u ukupnoj teritoriji bila iznad Španije i Portugala. Makija i alepski bor u "
      "zaleđu primorja izuzetno su zapaljivi pri visokom indeksu požarnog vremena i sporo se "
      "oporavljaju; poslije požara na strmim terenima slijedi erozija i pojačano oticanje, pa "
      "posljedica jednog ljeta stiže na naplatu tokom naredne kišne sezone."),
    P("Do 2030. sezona se produžava na oba kraja, a broj dana sa indeksom u kategoriji „vrlo visok” i "
      "„ekstreman” raste. Time se mijenja i logika odbrane: sistemi dimenzionisani za nekoliko "
      "kritičnih nedjelja u julu i avgustu moraju biti spremni od maja do oktobra."),
    H3("Turizam"),
    P("Turizam je za Crnu Goru najveći ekonomski ulog i ima dvije suprotstavljene izloženosti. Jul i "
      "avgust postaju manje udobni, sa toplotnim stresom koji se u gradskim sredinama ne prekida ni "
      "noću, dok maj, jun, septembar i oktobar postaju bolji nego ikad. Sezona kupanja se produžava: "
      "more sa 20 °C i više danas traje bliže pet i po nego četiri mjeseca."),
    P("Empirijski je već zabilježeno pomjeranje ka prelaznim mjesecima u zapadnom Sredozemlju. Za "
      "regionalne destinacije se do 2030. projektuje osjetan porast broja veoma vrelih dana; za "
      "Antaliju se, na primjer, procjenjuje petnaest dodatnih dana godišnje sa maksimumom preko "
      "37 °C. Ekonomski, to nije nužno gubitak: destinacija koja ima infrastrukturu za devet mjeseci "
      "rada zarađuje više od one koja ima gužvu u dva mjeseca i praznu obalu u ostalih deset. Ali "
      "prelazak na takav model traži vodu, saobraćaj i radnu snagu raspoređene drugačije nego danas."),
    H3("Zdravlje"),
    P("Toplota je u Evropi vodeći klimatski uzrok smrtnosti. Između 1991. i 2020. broj smrtnih "
      "slučajeva povezanih sa toplotom bio je šest puta veći u južnoj nego u śevernoj Evropi, a "
      "projekcije pokazuju da će južne regije nositi i najveći dodatni teret. Za zapadni Balkan se "
      "procjenjuje porast smrtnosti povezane sa toplotom od oko 20 %. Najizloženiji su stariji od 65 "
      "godina, hronični bolesnici, radnici na otvorenom i stanovnici gradskih dijelova bez zelenila."),
    P("Do 2030. najveća razlika neće doći od klime nego od pripreme. Zemlje koje su uvele sisteme "
      "ranog upozoravanja na toplotne talase, planove za domove za stare i prilagođeno radno vrijeme "
      "u građevinarstvu smanjile su smrtnost i pri jednakim temperaturama. Crna Gora takav sistem "
      "nema u operativnom obliku."),
    H3("More i obala"),
    P("Jadran se zagrijava među najbržima u Sredozemlju. Posljedice do 2030. su morski toplotni talasi "
      "skoro svake godine, ubrzano naseljavanje toplovodnih vrsta sa juga, pomor školjki u "
      "uzgajalištima u epizodama produžene toplote i sve duže prisustvo meduza. Podizanje nivoa mora "
      "do 2030. mjeriće se u centimetrima i samo po sebi neće ništa preplaviti, ali se sabira sa "
      "olujnim usponom i astronomskom plimom, pa pomjera povratni period plavljenja niskih djelova "
      "obale, prije svega u Boki i na ušću Bojane."),
    P("Erozija plaža je konkretniji problem od nivoa mora. Plaže na primorju su uske, često "
      "vještački nasute i pritisnute građevinama do same linije mora, pa nemaju gdje da se povuku. "
      "Svaka jača epizoda juga odnese dio pijeska koji se zatim mora nadoknaditi o javnom trošku."),

    H2("Novac"),
    P("Svjetska banka je u izvještaju o klimi i razvoju za Crnu Goru, objavljenom u decembru 2024, "
      "procijenila da bi klimatske nepogode mogle smanjiti bruto domaći proizvod za 7,9 % do 2050. "
      "godine. Poplave su najrazornija pojedinačna opasnost: pogađaju oko 10 000 ljudi godišnje i "
      "prośečno nanose 90 miliona dolara štete. Predloženi početni paket prilagođavanja za Crnu Goru "
      "procijenjen je na 5,7 milijardi dolara u cijenama iz 2020, sa težištem na mjerama koje treba "
      "sprovesti do 2030."),
    P("Odnos je poznat iz svake analize troškova i koristi u ovoj oblasti: uloženo u prevenciju vraća "
      "se višestruko u izbjegnutoj šteti, ali se vraća tiho i bez datuma, dok se šteta vidi odmah i "
      "sa slikom. To je politički razlog zašto se prilagođavanje odlaže, i on nije crnogorska "
      "specifičnost."),

    H2("Politika i obaveze"),
    P("Crna Gora je ažuriranim nacionalno utvrđenim doprinosom preuzela obavezu smanjenja emisija "
      "gasova sa efektom staklene bašte za 35 % do 2030. godine. Kao zemlja kandidat, obavezana je i "
      "na usklađivanje sa klimatskim zakonodavstvom Evropske unije, uključujući mehanizam za "
      "prekogranično prilagođavanje cijene ugljenika, koji od 2026. direktno pogađa izvoz "
      "energetski intenzivnih proizvoda iz regiona. Elektroprivredna proizvodnja iz uglja u Pljevljima "
      "je najveća pojedinačna stavka u tom računu."),
    P("Za horizont do 2030, međutim, smanjenje emisija u regionu ne mijenja lokalnu klimu — regionalni "
      "udio u globalnim emisijama je premali da bi se to izmjerilo. Ono mijenja cijenu izvoza, "
      "pristup fondovima i kvalitet vazduha, koji je u zimskim mjesecima u Pljevljima, Nikšiću i "
      "Podgorici među najgorima u Evropi. To su valjani razlozi sami po sebi, ali ih treba razdvojiti "
      "od prilagođavanja, koje jedino i djeluje na ono što će se ovdje osjetiti do 2030."),

    H2("Šta bi promijenilo ovu sliku"),
    P("Tri stvari mogu pomjeriti procjenu za narednih pet godina. Prva je veliki vulkanski erupcijski "
      "događaj, koji bi na dvije do tri godine spustio globalnu temperaturu za jednu do dvije "
      "desetine stepena i privremeno prekinuo niz rekordnih godina. Druga je brže od očekivanog "
      "slabljenje atlantske meridionalne cirkulacije, koje bi promijenilo raspored zimskih obrazaca "
      "nad Evropom na način koji današnji modeli ne opisuju pouzdano. Treća je smanjenje aerosolskog "
      "zagađenja iz brodskog saobraćaja i azijske industrije, koje uklanja rashladni efekat i "
      "ubrzava zagrijavanje više nego što je uračunato; taj efekat je od 2020. već vidljiv u podacima "
      "i predmet je otvorene rasprave."),
    P("Nijedna od te tri stvari ne mijenja smjer. Sve tri mijenjaju brzinu."),

    H2("Šta se konkretno može uraditi do 2030"),
    BULLETS([
        "Smanjiti gubitke u vodovodnoj mreži primorja sa 30–45 % na ispod 25 %. To je najveća i "
        "najjeftinija rezerva vode koju region ima.",
        "Uvesti operativni sistem ranog upozoravanja na toplotne talase, sa protokolom za domove za "
        "stare, bolnice i rad na otvorenom. Ista temperatura, uz pripremu, ubija znatno manje.",
        "Napraviti katastar bujičnih tokova i propusta na primorju i uskladiti ih sa današnjim, a "
        "ne sa nekadašnjim intenzitetom padavina.",
        "Uslovljavati nove turističke kapacitete rješenim vodosnabdijevanjem i odvođenjem otpadnih "
        "voda u vršnoj sezoni, a ne u prośeku godine.",
        "Prebaciti upravljanje šumama sa gašenja na prevenciju: prośeke, čišćenje makije oko naselja "
        "i obnova požarišta prije prve kišne sezone.",
        "Proširiti mrežu mjerenja i objaviti podatke. Sve što je u ovom dokumentu izračunato iz "
        "reanalize bilo bi tačnije da su stanični nizovi javno dostupni u mašinski čitljivom obliku.",
    ]),

    H2("Zaključak"),
    P("Do 2030. Balkan ostaje isto mjesto sa drugačijim rasporedom. Ljeto duže i vrelije, sa "
      "unutrašnjošću koja se zagrijava brže od obale i sa noćima koje se ne hlade. Zima blaža i "
      "kišovitija, sa manje snijega ispod 1400 m. Padavine ukupno slične, ali skoncentrisane u manji "
      "broj jačih epizoda, što istovremeno znači i više suše i više poplava. More toplije skoro svake "
      "godine, sa sezonom kupanja koja se rasteže do novembra i sa ekosistemom koji se mijenja brže "
      "nego što ga stižemo popisati."),
    P("Ništa od toga nije nova informacija za nekoga ko ovdje živi. Novo je to što se sada može "
      "izmjeriti i staviti u projekat, umjesto da se prepričava kao utisak da su ljeta nekad bila "
      "blaža. Pet godina je kratak rok za smanjenje emisija i sasvim dovoljan za vodovod, plan "
      "toplotnog talasa i propust ispod magistrale."),

    H2("Izvori"),
    SOURCES([
        "Copernicus Climate Change Service, European State of the Climate 2025, 29. april 2026.",
        "Copernicus Climate Change Service, bilten o površinskoj temperaturi za jul 2026.",
        "Mercator Ocean International, bilteni o temperaturi okeana i morskim toplotnim talasima, 2026.",
        "Zajednički istraživački centar Evropske komisije, izvještaj o suši, vodostajima i požarima, "
        "12. avgust 2026.",
        "EFFIS, statistika izgorjele površine za sezone 2025. i 2026.",
        "WMO, Global Annual to Decadal Climate Update 2026–2030.",
        "MedECC, Prvi mediteranski izvještaj o procjeni (MAR1) i posebni izvještaji o obalnim zonama "
        "i o vezi voda–energija–hrana–ekosistemi.",
        "IPCC, Šesti izvještaj o procjeni, radna grupa II, Cross-Chapter Paper 4: Mediterranean Region.",
        "Svjetska banka, Country Climate and Development Report za zapadni Balkan i Crnu Goru, 2024.",
        "Crna Gora, ažurirani nacionalno utvrđeni doprinos i nacionalni izvještaji prema UNFCCC.",
        "Lancet Public Health (2024), Temperature-related mortality burden and projected change in "
        "1368 European regions.",
        "ERA5 reanaliza preko Open-Meteo arhive, tačke Budve i Podgorice, 1950–2026.",
    ]),
]


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "20_VIII_MMXXVI_balkan_2030.pdf")
    build(out, RUNNING, TITLE, SUBTITLE, META, BLOCKS)
    print(out)
