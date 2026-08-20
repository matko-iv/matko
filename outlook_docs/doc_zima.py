# -*- coding: utf-8 -*-
"""Sezonski dokument: zima 2026/2027, Budva i crnogorsko primorje."""

from docgen import BULLETS, H2, H3, P, SOURCES, TABLE, build

RUNNING = "Sezonski dokument — zima 2026/2027, Budva i primorje"

TITLE = "Zima 2026/2027 nad Budvom i crnogorskim primorjem"
SUBTITLE = ("Sezonska procjena temperature, padavina, mora i rizika, uz vrlo jak El Niño "
            "u pozadini")

META = ("Referentna tačka: Budva (42,28° SGŠ, 18,84° IGD), sa primjenjivošću na pojas Herceg Novi "
        "— Ulcinj i njegovo zaleđe. Period pokrivenosti: decembar 2026 — februar 2027 (DJF), sa "
        "osvrtom na mart 2027. Datum izrade: 20. avgust 2026. Referentna klimatologija: 1991–2020, "
        "računata iz ERA5 reanalize za navedenu tačku. Ovo je prva verzija dokumenta za zimu "
        "2026/2027; prozor revizije je 15. oktobar 2026, kada izlaze sezonske najave inicijalizovane "
        "1. oktobra i kada se vidi vrhunac El Niña.")

BLOCKS = [
    H2("Izvršni sažetak"),
    P("Zima 2026/2027. dolazi sa najjačim El Niñom otkad se mjeri i sa Sredozemljem koje je u julu "
      "2026. imalo najtopliju površinu mora u istoriji zapisa. Ta dva podatka ne daju istu poruku. "
      "El Niño je snažan signal koji se u Evropi slabo i neuredno prevodi, a toplo more je slab "
      "signal koji djeluje neprekidno i lokalno. Za primorje Crne Gore, najizgledniji ishod je zima "
      "toplija od prośeka za +1,0 ± 0,8 °C u odnosu na razdoblje 1991–2020, sa padavinama u rasponu "
      "110 ± 30 % normale i sa težištem na jugu i sredozemnim ciklonama, a ne na hladnim upadima."),
    P("Konkretno se očekuje: DJF srednja temperatura oko 9,5 °C na tački Budve umjesto klimatoloških "
      "8,5 °C; ukupne padavine 720 ± 200 mm umjesto 656 mm; snijeg na samoj obali vrlo malo vjerovatan; "
      "u planinskom zaleđu iznad 1200 m snijega oko ili iznad prośeka, ali sa kasnim početkom sezone i "
      "sa granicom snijega koja u svakom prolasku ciklone ide visoko. Najveći pojedinačni rizik nije "
      "temperatura nego voda: vjerovatnoća bar jednog dana sa preko 100 mm kiše u 24 h na primorju "
      "procijenjena je na 25 %, prema klimatoloških 10 %."),
    P("Drugi rizik je suprotan prvom i ne isključuje ga. Sve tri dosad zabilježene zime sa vrlo jakim "
      "El Niñom imale su u januaru ili februaru nagli prelazak śevernoatlantske oscilacije u negativnu "
      "fazu. U ovdašnjim uslovima to znači kratak, oštar prodor hladnog vazduha, mraz u zaleđu i "
      "mogućnost snijega do obale u trajanju od dva do četiri dana. Takav događaj se ne može zakazati "
      "mjesecima unaprijed, a u sezonskom prośeku se jedva vidi."),
    P("Pouzdanost. Temperaturni dio ove najave je umjereno pouzdan i naslanja se na trend, na toplo "
      "more i na saglasnost modela. Padavinski dio je slab i treba ga čitati kao tendenciju. Evropa "
      "je, po vještini sezonske prognoze, najgori kontinent na svijetu, a zima je sezona u kojoj se ta "
      "slabost najviše vidi."),

    H2("Podaci, metodologija i ograničenja"),
    P("Klimatologija i istorijski nizovi u ovom dokumentu računati su iz ERA5 reanalize za tačku "
      "42,28° SGŠ, 18,84° IGD, preko Open-Meteo arhive, za period 1950–2026. ERA5 je mreža rezolucije "
      "oko 9 km i miješa more i kopno, pa su noćni minimumi na ovoj tački viši, a padavine veće nego "
      "na stanici Bar. Godišnji zbir padavina na ovoj tački iznosi 2108 mm za 1991–2020, što je "
      "orografski uvećana vrijednost i ne treba je porediti sa stanicom. Poređenja unutar samog niza "
      "(anomalije, rangovi, odnosi prema normali) su korektna, jer ista pristrasnost pogađa i "
      "klimatologiju i pojedinačnu godinu."),
    P("Sezonski signal je uzet iz sezonske najave službe Copernicus (C3S) izdate u avgustu 2026, iz "
      "dijagnostičke rasprave o ENSO-u Centra za prognozu klime NOAA od 13. avgusta 2026, iz pregleda "
      "IRI Columbia za avgust 2026, iz biltena o okeanu Mercator Ocean International i iz biltena o "
      "suši i požarima Zajedničkog istraživačkog centra Evropske komisije. Analogne zime izabrane su po "
      "jednom kriterijumu — vrhunac ONI iznad +2,0 °C — i njihove lokalne vrijednosti su izračunate, "
      "a ne prepričane."),
    P("Ograničenja su ozbiljna i navode se prije zaključaka, ne poslije njih. Prvo, veza između "
      "tropskog Pacifika i evropske zime je posredna, ide preko stratosfere i preko Śevernog Atlantika, "
      "i nije stacionarna — ista jačina El Niña davala je različit evropski odgovor u različitim "
      "decenijama. Drugo, vještina sezonske prognoze padavina nad jugoistočnim Sredozemljem je tek "
      "neznatno iznad klimatologije. Treće, uzorak vrlo jakih El Niño zima broji tri slučaja, što je "
      "premalo za statistiku i dovoljno samo za ilustraciju. Četvrto, sve brojke u mjesečnim tabelama "
      "su rasponi, jer sezonska najava koja daje jednu decimalu za pojedinačni mjesec obmanjuje "
      "korisnika."),

    H2("Polazno stanje: ljeto koje prethodi"),
    P("Zima se ne nasljeđuje na praznom. Jul 2026. bio je najtopliji jul u zapisu za Sredozemno more, "
      "sa prośečnom temperaturom površine 27,07 ± 0,27 °C, iznad rekorda iz jula 2025. (26,68 ± "
      "0,11 °C). Vanpolarni okean između 60° JGŠ i 60° SGŠ imao je 20,96 °C, najviše ikad za taj "
      "mjesec, iznad 20,89 °C iz 2023. Globalna prizemna temperatura u julu 2026. iznosila je 16,90 °C, "
      "0,67 °C iznad prośeka 1991–2020 i 1,47 °C iznad procijenjenog predindustrijskog nivoa."),
    P("Na kopnu, Evropa je ljeto 2026. dočekala i ispratila u suši. Sredinom avgusta 50 % teritorije "
      "Evropske unije i Ujedinjenog Kraljevstva bilo je u nekoj od kategorija suše, a 9 % u kategoriji "
      "„alarm”. Loara, Po, Rajna i Dunav zabilježili su rekordno niske vodostaje; Rajna je kod Kelna "
      "pala na 74 cm, a Dunav do granice plovnosti, zbog čega je rafinerija u Pančevu 4. avgusta "
      "prepolovila preradu. Do 5. avgusta u Evropi je izgorjelo 505 683 ha, prema 379 392 ha do istog "
      "datuma 2025. Crna Gora je, mjereno udjelom izgorjele u ukupnoj teritoriji, prošla gore od "
      "Španije i Portugala."),
    P("Za zimu su iz ovoga važne dvije stvari. Tlo u zaleđu ulazi u kišnu sezonu isušeno i sa "
      "oštećenim biljnim pokrivačem na požarištima, što znači brže oticanje i veći rizik od bujica i "
      "klizišta pri prvim jakim kišama. I more je toplije nego ikad u ovo doba godine, pa svaka "
      "ciklona koja se u jesen i ranu zimu formira nad južnim Jadranom raspolaže većom količinom "
      "vodene pare — po Klauzijus-Klapejronovoj relaciji oko 7 % više vlage po stepenu zagrijavanja."),

    H2("El Niño: stanje sistema u avgustu 2026"),
    P("Događaj je već sada vrlo jak i još jača. Julske vrijednosti indeksa bile su +1,4 °C u regionu "
      "Niño 3.4, +1,7 °C u regionu Niño 3 i +2,9 °C u regionu Niño 1+2, dakle sa naglaskom na istočni "
      "Pacifik, što odgovara tipu iz 1982/83. i 1997/98. Podpovršinske anomalije dosezale su +10 °C, "
      "a oba indeksa južne oscilacije bila su oko dvije standardne devijacije ispod nule tokom jula. "
      "Sedmične vrijednosti u avgustu razlikuju se po proizvodu: +2,7 °C prema proizvodu koji koristi "
      "NOAA i +2,20 °C prema relativnom indeksu australijskog biroa za sedmicu koja se završila "
      "9. avgusta. Razlika nije greška nego posljedica različite osnove i različite obrade; smjer je "
      "isti."),
    TABLE("Tabela 1. Stanje i projekcija ENSO sistema, prema dijagnostičkoj raspravi NOAA CPC od "
          "13. avgusta 2026. i pregledu IRI Columbia za avgust 2026. RONI je relativni indeks, koji od "
          "anomalije u regionu Niño 3.4 oduzima zagrijavanje cijelog tropskog pojasa i zato je "
          "uporediviji kroz decenije od klasičnog ONI.",
          ["Veličina", "Vrijednost", "Izvor i datum"],
          [["Niño 3.4, jul 2026", "+1,4 °C", "NOAA CPC, 13.8.2026"],
           ["Niño 3, jul 2026", "+1,7 °C", "NOAA CPC, 13.8.2026"],
           ["Niño 1+2, jul 2026", "+2,9 °C", "NOAA CPC, 13.8.2026"],
           ["Podpovršinska anomalija", "do +10 °C", "NOAA CPC, 13.8.2026"],
           ["RONI, medijana za okt–dec 2026", "+2,66 °C (sredina raspodjele +2,37 do +2,95)",
            "NOAA CPC, 13.8.2026"],
           ["RONI, medijana za dec–feb", "+2,23 °C", "NOAA CPC, 13.8.2026"],
           ["Izgledi za istorijski događaj (≥ +2,5 °C, okt–dec)", "69 %", "NOAA CPC, 13.8.2026"],
           ["Izgledi za vrlo jak događaj u jesen i zimu", "preko 90 %", "NOAA CPC, 13.8.2026"],
           ["Vjerovatnoća da El Niño traje kroz feb–apr 2027", "100 %", "IRI, avgust 2026"],
           ["Modeli koji daju vrhunac ≥ +3,0 °C", "15 od 26", "IRI plume, avgust 2026"],
           ["Indeks dipola Indijskog okeana", "+0,41 °C, treća sedmica iznad praga",
            "BoM, 9.8.2026"]],
          widths=[34, 34, 32]),
    P("Uz El Niño se razvija i pozitivan dipol u Indijskom okeanu. Ta dva obrasca zajedno pojačavaju "
      "tropsko forsiranje cirkulacije śeverne hemisfere i, u praksi, znače da će atmosferski odgovor "
      "biti jači nego što bi sama vrijednost u Pacifiku sugerisala. Kvazidvogodišnja oscilacija u "
      "stratosferi je u zapadnoj fazi, sa zapadnim vjetrovima koji se spuštaju kroz nivo 15–30 hPa i "
      "koji bi do zime trebalo da se ustale na 30–50 hPa. Zapadna faza smanjuje izglede za naglo "
      "zagrijavanje stratosfere u odnosu na istočnu, pa se dvije sklonosti — El Niño koji povećava "
      "rizik i zapadna kvazidvogodišnja faza koja ga smanjuje — djelimično poništavaju."),

    H2("Kako El Niño uopšte stigne do Jadrana"),
    P("Put je dug i na svakom koraku gubi na jačini. Pomjeranje tropskih oborina na istok mijenja "
      "raspored uzlaznih strujanja, iz njih se dižu planetarni Rosbijevi talasi, ti talasi se šire ka "
      "polu i naviše, dio energije ulazi u stratosferu i slabi polarni vrtlog, a oslabljeni vrtlog se "
      "mjesec do dva kasnije spusti u troposferu kao negativna faza arktičke i śevernoatlantske "
      "oscilacije. Tek na tom kraju lanca stoji naše vrijeme."),
    P("Zbog te dužine, evropski odgovor na El Niño ima dvije faze i one su suprotne. U ranoj zimi, "
      "decembru i prvoj polovini januara, prevlađuje pojačan zapadni tok, blaga i vlažna klima nad "
      "zapadnom i južnom Evropom i natprośečne padavine u śevernom Sredozemlju. U kasnoj zimi, "
      "februaru i martu, češće se javlja negativna faza śevernoatlantske oscilacije, blokada nad "
      "śevernom Evropom i prodori hladnog vazduha ka jugu. Taj kasnozimski obrazac opisao je "
      "Brönnimann (2007, Reviews of Geophysics) na osnovu petovjekovnih rekonstrukcija, a "
      "stratosferski mehanizam koji ga nosi razradili su Ineson i Scaife (2009, Nature Geoscience) i "
      "Ayarzagüena i saradnici (2018, Climate Dynamics). Noviji radovi pokazuju da jačina te veze "
      "varira od decenije do decenije, što je razlog zašto je operativno koristiti je kao rizik, a ne "
      "kao prognozu."),
    P("Za jugoistočni Jadran, obje faze imaju istu praktičnu posljedicu na padavine, a suprotnu na "
      "temperaturu. Rani zimski zapadni tok donosi kišu preko fronta; kasnozimska blokada donosi "
      "sredozemne ciklone koje se sporo kreću i koje na dinarsku barijeru izlijevaju velike količine "
      "vode uz istovremeno zahlađenje. Godina sa jakim El Niñom u ovim krajevima rijetko je suva "
      "zima. Rijetko je i mirna."),

    H2("Multi-modelska slika za DJF 2026/2027"),
    P("Sezonska najava službe Copernicus izdata u avgustu 2026. stavlja veći dio Evrope iznad 80. "
      "percentila istorijske raspodjele temperature, uz izuzetak najistočnijih i najśevernijih "
      "djelova kontinenta, i daje signal za vlažniju jesen na jugu i zapadu, uz izričitu napomenu da "
      "je nesigurnost tu veća a vještina niža nego u tropima. Raspored pritiska koji modeli daju za "
      "zimu je greben visokog pritiska sa juga i ciklonalna aktivnost nad śeverozapadom kontinenta, "
      "dakle pojačan zapadni tok, sa vlagom i natprośečnim padavinama."),
    TABLE("Tabela 2. Konsolidacija sezonskog signala za DJF 2026/2027 nad jugoistočnim Jadranom. "
          "Vrijednosti su ekspertska sinteza objavljenih kartografskih i tekstualnih proizvoda, a ne "
          "numerički izlaz pojedinačnog modela; tamo gdje pojedinačni sistemi ne objavljuju brojke za "
          "tačku, dat je raspon konzistentan sa objavljenim tercilnim kartama.",
          ["Izvor", "Temperatura DJF", "Padavine (% normale)", "Pouzdanost"],
          [["C3S multi-model (avgust 2026)", "iznad 80. percentila", "iznad prośeka na jugu i zapadu",
            "srednja (T) / niska (P)"],
           ["ECMWF SEAS5", "+0,8 do +1,8 °C", "100 do 130 %", "srednja"],
           ["UKMO GloSea6", "+0,5 do +1,5 °C", "100 do 125 %", "srednja"],
           ["Météo-France System 9", "+0,8 do +1,6 °C", "105 do 135 %", "srednja"],
           ["DWD GCFS, CMCC SPS, NCEP CFSv2", "+0,5 do +1,5 °C", "95 do 130 %", "srednja-niska"],
           ["Analogni kompozit (4 zime)", "−0,1 do +1,8 °C", "92 do 194 %", "ilustrativna"],
           ["Konsolidovana procjena", "+1,0 ± 0,8 °C", "110 ± 30 %", "srednja (T) / niska (P)"]],
          widths=[30, 22, 26, 22]),
    P("Raspon analognog kompozita je namjerno ostavljen širok. On pokriva zimu koja je dala 91 % "
      "normale i zimu koja je dala 194 % normale, i upravo ta širina je poštena mjera onoga što se o "
      "padavinama zna unaprijed."),

    H2("Analogne zime"),
    P("Postoje tri zime sa vrhuncem indeksa ONI iznad +2,0 °C: 1982/83, 1997/98. i 2015/16. Uz njih "
      "se posmatra i 2009/10, umjeren El Niño sa izrazito negativnom śevernoatlantskom oscilacijom, "
      "jer je to lokalno najvlažnija zima u cijelom nizu. Vrijednosti su izračunate iz ERA5 za tačku "
      "Budve i date su kao odstupanje od klimatologije 1991–2020."),
    TABLE("Tabela 3. Analogne zime na tački Budve, ERA5, odstupanje srednje temperature i procenat "
          "normale padavina po mjesecima. Zima je označena godinom januara. Zima 2009/10 je "
          "najvlažnija u nizu 1950–2026 sa 1271 mm, a zima 2015/16 sadrži gotovo suv decembar (1 % "
          "normale) praćen vrlo vlažnim februarom.",
          ["Zima", "ONI vrhunac", "decembar", "januar", "februar", "DJF ukupno"],
          [["1982/83", "+2,2 °C", "+0,8 °C / 144 %", "+0,7 °C / 41 %", "−2,2 °C / 130 %",
            "−0,1 °C / 112 %"],
           ["1997/98", "+2,4 °C", "+0,2 °C / 127 %", "+1,2 °C / 78 %", "+1,6 °C / 54 %",
            "+1,0 °C / 92 %"],
           ["2009/10", "+1,6 °C", "+1,0 °C / 175 %", "−0,1 °C / 185 %", "+0,1 °C / 219 %",
            "+0,4 °C / 194 %"],
           ["2015/16", "+2,6 °C", "+1,4 °C / 1 %", "+0,5 °C / 157 %", "+3,3 °C / 155 %",
            "+1,8 °C / 94 %"]],
          widths=[14, 13, 19, 18, 18, 18]),
    P("Iz tabele se vidi ono što prośek krije. Nijedna od četiri zime nije bila ravna: svaka je imala "
      "bar jedan mjesec sa manje od 60 % ili više od 150 % normale, a dvije su imale i jedno i drugo. "
      "Februar 1983. bio je 2,2 °C hladniji od današnje klimatologije, februar 2016. bio je 3,3 °C "
      "topliji. Ista pojava u Pacifiku, obrnut ishod na Jadranu. Zato se ovaj dokument bavi rasporedom "
      "vjerovatnoća, a ne rasporedom dana."),
    P("Vrijedi dodati i kontekst zagrijavanja. Trend srednje zimske temperature na tački Budve iznosi "
      "+0,19 °C po deceniji za period 1951–2026, a godišnji +0,21 °C. Šest od osam najtoplijih zima u "
      "nizu od 1950. dogodilo se poslije 2014. godine; najtoplija je 2023/24. sa +2,0 °C iznad "
      "klimatologije. Za zimu 2026/2027. to znači da je „iznad prośeka” danas skoro osnovno stanje, a "
      "ne prognostička hrabrost."),

    H2("Mjesečni pregled"),
    P("Klimatologija u tabeli je izračunata iz ERA5 za tačku Budve, period 1991–2020. Centralna "
      "procjena i raspon odnose se na zimu 2026/2027. Raspon pokriva 80 % ishoda, dakle jedan od pet "
      "mjeseci će po definiciji izaći iz njega."),
    TABLE("Tabela 4. Klimatologija 1991–2020 i procjena za zimu 2026/2027, tačka Budve, ERA5. "
          "Padavine su date kao raspon jer je mjesečni zbir na ovoj obali određen sa dva do četiri "
          "pojedinačna događaja, pa mu je varijansa velika i u klimatologiji.",
          ["Mjesec", "Tmax klima", "Tmin klima", "Padavine klima", "Procjena 2026/27"],
          [["decembar", "11,8 °C", "6,9 °C", "269 mm",
            "srednja T +0,5 do +1,5 °C; padavine 220–380 mm; jugo često"],
           ["januar", "10,6 °C", "5,3 °C", "191 mm",
            "srednja T 0 do +1,5 °C; padavine 150–330 mm; najveći rizik od preokreta"],
           ["februar", "11,4 °C", "5,4 °C", "205 mm",
            "srednja T +0,5 do +2,0 °C; padavine 160–340 mm; blokade i sredozemne ciklone"],
           ["mart", "14,1 °C", "7,6 °C", "193 mm",
            "srednja T +0,5 do +2,0 °C; padavine 140–280 mm; rana vegetacija, rizik od mraza"]],
          widths=[13, 14, 14, 16, 43]),
    P("Decembar 2026. najvjerovatnije počinje blago i vlažno, sa zapadnim tokom i sa prvim "
      "sredozemnim ciklonama koje se hrane rekordno toplim morem. Snijeg u planinskom zaleđu kasni; "
      "granica snijega pri prolascima fronta ide iznad 1400 m, pa se u Kolašinu i na Žabljaku prvi "
      "stabilan pokrivač očekuje kasnije nego obično. Januar 2027. nosi najveću neizvjesnost: "
      "polovina analognih zima ima u tom mjesecu preokret u negativnu fazu oscilacije, a druga "
      "polovina nastavak blagog toka. Februar 2027. je mjesec u kojem se, po istorijskom obrascu, "
      "najčešće javlja kasnozimska blokada, pa uz visoku srednju temperaturu treba računati i na "
      "mogućnost kratkog oštrog zahlađenja. Mart 2027. najvjerovatnije donosi ranu i toplu vegetacionu "
      "sezonu, sa rizikom da kasni mraz pogodi već probuđene voćke u Crmnici i Zeti."),

    H2("Vjerovatnoće prekoračenja pragova"),
    P("Klimatološka osnova je udio zima u periodu 1991–2020. u kojima se događaj javio bar jednom, "
      "izračunat iz ERA5 za tačku Budve. Procjena za 2026/2027. je konsolidacija te osnove, sezonskog "
      "signala i analognog kompozita."),
    TABLE("Tabela 5. Vjerovatnoće prekoračenja pragova za zimu 2026/2027, primorje Crne Gore. "
          "Klimatološka osnova je izračunata, a procjena je ekspertska. Pragovi za padavine odnose se "
          "na ERA5 tačku i sistematski su viši nego što bi bili na stanici; odnos između klimatologije "
          "i procjene ostaje valjan.",
          ["Prag ili događaj", "Klimatološka osnova", "Procjena za DJF 2026/27"],
          [["Srednja zimska temperatura iznad +1 °C od normale", "23 % zima", "55 %"],
           ["Srednja zimska temperatura iznad +1,5 °C od normale", "7 % zima", "30 %"],
           ["Bar jedan dan sa ≥ 50 mm kiše", "83 % zima", "90 %"],
           ["Tri ili više dana sa ≥ 50 mm kiše", "37 % zima", "50 %"],
           ["Bar jedan dan sa ≥ 100 mm kiše", "10 % zima", "25 %"],
           ["Ukupne padavine iznad 120 % normale", "23 % zima", "40 %"],
           ["Ukupne padavine iznad 150 % normale", "10 % zima", "20 %"],
           ["Ukupne padavine ispod 80 % normale", "20 % zima", "12 %"],
           ["Bar jedan mraz na obali (Tmin < 0 °C)", "73 % zima", "60 %"],
           ["Deset ili više mraznih dana", "3 % zima", "5 %"],
           ["Snijeg koji se zadrži na obali", "oko 10 % zima", "12 %"],
           ["Prodor hladnog vazduha sa negativnom fazom NAO u jan–feb", "oko 40 % zima", "55 %"]],
          widths=[46, 26, 28]),
    P("Dva reda iz tabele nose gotovo cijelu operativnu poruku. Vjerovatnoća dana sa preko 100 mm "
      "kiše podignuta je sa 10 na 25 % zato što se toplo more, pojačan zapadni tok i sklonost ka "
      "sporim sredozemnim ciklonama sabiraju u istom smjeru. Vjerovatnoća hladnog prodora podignuta je "
      "sa 40 na 55 % zbog obrasca kasne zime u analognim godinama, uprkos tome što je sezonski prośek "
      "topao."),

    H2("Sektorski rizici"),
    H3("Bujice, klizišta i kanalizacija"),
    P("Ovo je glavni rizik sezone. Zaleđe primorja ulazi u kišni dio godine sa isušenim tlom i sa "
      "požarištima iz ljeta 2026, na kojima nema vegetacije koja bi zadržala vodu. Prva jaka kiša na "
      "takvoj podlozi daje veći i brži oticaj nego ista kiša na neoštećenom terenu. Kritične tačke su "
      "poznate: Grbaljsko polje, bujični tokovi iznad Budve i Bečića, Petrovac i Buljarica, spustovi "
      "prema Sutomoru. Sistemi za odvođenje kišnice u Budvi dimenzionisani su za drugačiju "
      "raspodjelu padavina i u epizodama preko 60 mm/h redovno se preplavljuju."),
    H3("Vodosnabdijevanje i akumulacije"),
    P("Vlažna zima je za primorje dobra vijest, ali sa odloženim dejstvom. Izvorišta se pune sporo i "
      "prazne brzo, a ljeto 2027. zavisi od toga koliko će padavina pasti između novembra i marta. "
      "Ako se ostvari donji dio raspona, dakle oko 80 % normale, ulazi se u naredno ljeto sa "
      "deficitom, a ljeto poslije jakog El Niña obično je toplo. To je scenario koji zaslužuje "
      "praćenje već od januara."),
    H3("More, talasi i obala"),
    P("Češće i jače jugo znači duže epizode visokog talasa u Budvanskom zalivu i pojačanu eroziju "
      "plaža u Bečićima, Rafailovićima i Sutomoru, gdje je pijesak već pod pritiskom. Uz to ide i "
      "podignut nivo mora u epizodama niskog pritiska i juga, koji sa astronomskom plimom daje "
      "plavljenje niskih djelova obale, najizraženije u Boki."),
    H3("Snijeg i planinski turizam"),
    P("Signal za planine je podijeljen. Ukupna količina padavina iznad prośeka pomaže, temperatura "
      "iznad prośeka odmaže. Rezultat je sezona sa dobrim snijegom iznad 1500 m i nesigurnim snijegom "
      "između 1000 i 1400 m, dakle upravo tamo gdje se nalazi većina crnogorskih staza. Vjerovatan "
      "je kasan početak sezone i oslanjanje na vještački snijeg u decembru, uz mogućnost velikih "
      "sniježnih količina u pojedinačnim epizodama u januaru i februaru. Isti obrazac važi za veći "
      "dio Alpa, gdje se signal za snijeg pomjera ka śeveru i ka većim visinama."),
    H3("Poljoprivreda"),
    P("Blaga zima znači nedovoljan broj sati hlađenja za koštičave voćke, ranije kretanje vegetacije i "
      "veći rizik od mraza u martu i aprilu. Maslina i citrusi prolaze dobro u toploj zimi, ali "
      "maslinina muva i druge štetočine prezimljavaju u većem broju, pa raste pritisak na zaštitu. "
      "Vlažna zima pogoduje gljivičnim oboljenjima."),
    H3("Energetika i saobraćaj"),
    P("Potrošnja za grijanje biće ispod prośeka, ali su epizode juga sa udarima vjetra glavni uzrok "
      "kvarova na distributivnoj mreži u primorju. Jadranska magistrala je u epizodama obilne kiše "
      "izložena odronima, a u kratkim hladnim prodorima poledici na dionicama u zaleđu."),

    H2("Regionalna slika"),
    TABLE("Tabela 6. Regionalizacija signala za zimu 2026/2027. Poređenja su izvedena iz sezonske "
          "najave službe Copernicus i iz obrasca cirkulacije koji modeli daju, a ne iz nacionalnih "
          "sezonskih biltena, koji za zimu 2026/2027. u trenutku izrade još nijesu izdati.",
          ["Područje", "Temperatura", "Padavine i snijeg"],
          [["Crnogorsko primorje", "iznad prośeka", "iznad prośeka; snijeg na obali malo vjerovatan"],
           ["Crnogorske planine", "iznad prośeka", "padavine iznad prośeka; snijeg dobar iznad 1500 m"],
           ["Dalmacija i Hercegovina", "iznad prośeka", "iznad prośeka, sa težištem na jugu"],
           ["Panonski dio (Vojvodina, śeverna Srbija)", "blago iznad prośeka",
            "oko prośeka; magla i inverzije"],
           ["Alpi", "iznad prośeka", "snijeg ispod prośeka na nižim visinama"],
           ["Skandinavija i Škotska", "blizu prośeka do blago iznad", "vlažno, snijeg iznad prośeka na śeveru"],
           ["Istočna Evropa", "blizu prośeka", "veći rizik od blokade i hladnih upada"]],
          widths=[28, 22, 50]),

    H2("Šta bi opovrglo ovu najavu"),
    P("Sezonska najava koja ne kaže kako bi se pokazala pogrešnom nije upotrebljiva. Ova bi bila "
      "opovrgnuta u tri slučaja. Prvi: ako se El Niño u septembru i oktobru zaustavi ispod +2,0 °C u "
      "regionu Niño 3.4, čime bi otpao dio pretpostavke o jakom tropskom forsiranju. Drugi: ako se "
      "polarni vrtlog krajem novembra pokaže izrazito jakim i stabilnim, jer bi tada zima krenula u "
      "trajno pozitivnu fazu oscilacije, sa suvljim i vjetrovitijim jugom Evrope nego što je ovdje "
      "opisano. Treći: ako se do kraja decembra ostvari manje od 60 % normalnih padavina, čime bi "
      "pretpostavka o vlažnoj zimi izgubila osnov, po uzoru na decembar 2015. sa 1 % normale."),
    P("Prvi kontrolni datum je 10. septembar 2026, kada izlazi naredna dijagnostička rasprava NOAA. "
      "Drugi je početak oktobra, kada izlaze sezonske najave inicijalizovane 1. oktobra i kada se "
      "prvi put vidi zimski obrazac u modelima sa razumnim vremenom najave. Treći je sredina novembra, "
      "kada se stanje polarnog vrtloga može pratiti direktno."),

    H2("Zaključak"),
    P("Zima 2026/2027. na crnogorskom primorju najvjerovatnije će biti toplija i vlažnija od "
      "klimatološke, sa jugom kao vodećim vremenskim tipom, malo snijega na obali i dobrim snijegom "
      "samo na većim visinama. Iza tog prośeka stoje dvije stvari koje prośek ne pokazuje: povišen "
      "rizik od obilne kiše u kratkom vremenu, na tlu koje je poslije ljetnjih požara i suše manje "
      "sposobno da je primi, i realna mogućnost kratkog oštrog zahlađenja u januaru ili februaru, po "
      "obrascu koji su imale sve tri zime sa vrlo jakim El Niñom."),
    P("El Niño ove jačine je globalno rijedak događaj i biće vidljiv na mnogo mjesta. Na Jadranu neće "
      "biti vidljiv kao katastrofa nego kao raspored: više kiše u nekoliko epizoda, više juga, manje "
      "mraza i more koje ni u februaru neće biti hladno kao nekad."),

    H2("Izvori"),
    SOURCES([
        "NOAA Climate Prediction Center, ENSO Diagnostic Discussion, 13. avgust 2026.",
        "IRI Columbia, ENSO Quick Look i model plume, avgust 2026.",
        "Bureau of Meteorology (Australija), Climate Driver Update, 11. avgust 2026.",
        "Copernicus Climate Change Service, sezonske najave i mjesečni bilteni, avgust 2026.",
        "Copernicus Climate Change Service, bilten o površinskoj temperaturi za jul 2026.",
        "Mercator Ocean International, bilteni o temperaturi okeana i morskim toplotnim talasima, "
        "jul i avgust 2026.",
        "Zajednički istraživački centar Evropske komisije, izvještaj o suši, vodostajima i požarima, "
        "12. avgust 2026.",
        "EFFIS, statistika izgorjele površine za sezonu 2026.",
        "ERA5 reanaliza preko Open-Meteo arhive, tačka 42,28° SGŠ 18,84° IGD, 1950–2026.",
        "Brönnimann, S. (2007), Impact of El Niño–Southern Oscillation on European climate, "
        "Reviews of Geophysics 45, RG3003.",
        "Ineson, S. i Scaife, A. A. (2009), The role of the stratosphere in the European climate "
        "response to El Niño, Nature Geoscience 2, 32–36.",
        "Ayarzagüena, B. i saradnici (2018), Stratospheric role in interdecadal changes of El Niño "
        "impacts over Europe, Climate Dynamics 51, 3985–3998.",
    ]),
]


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "docs", "20_VIII_MMXXVI_zima.pdf")
    build(out, RUNNING, TITLE, SUBTITLE, META, BLOCKS)
    print(out)
