# -*- coding: utf-8 -*-
"""Ubacuje članak o Balkanu do 2030. i dopunjuje spisak izvora na stranici najava."""

import io
import os

PAGE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "docs", "dugorocne-najave.html")

ARTICLE = '''    <div class="article">
        <h2>Balkan do 2030: koliko je toga već zaključano</h2>
        <p class="meta">Objavljeno: 20.8.2026.</p>
        <p>
            Puni dokument, sa izmjerenim trendovima za Budvu i Podgoricu, projekcijama po sektorima i procjenom troška, možete otvoriti <a href="20_VIII_MMXXVI_balkan_2030.pdf">ovđe</a>.
        </p>

        <h3>Šta je već izmjereno</h3>
        <p>
            Evropa se u posljednjih trideset godina zagrijava po 0,56 °C na deceniju, dvostruko brže od globalnih 0,27 °C, i to je najbrže zagrijavanje bilo kojeg kontinenta. Sredozemno more ide po 0,41 °C na deceniju i u julu 2026. imalo je najtopliju površinu u istoriji mjerenja, 27,07 °C. Godišnja temperatura mora oko Evrope najviša je u zapisu četvrtu godinu zaredom.
        </p>
        <p>
            Lokalno se promjena ne vidi toliko u srednjoj temperaturi koliko u broju vrelih dana. Na tački Budve, broj dana sa maksimumom preko 30 °C porastao je sa 13 godišnje u razdoblju 1961–1990. na 44 u razdoblju 2011–2025. U Podgorici je sa 18 otišao na 67. Broj dana preko 35 °C u Podgorici je u istom poređenju porastao sa jednog na osamnaest. Tropskih noći na primorju sada ima preko devedeset godišnje, prema šezdeset i tri u šezdesetim.
        </p>
        <figure class="fig">
  <figcaption class="fig-title">Dani sa najvišom dnevnom temperaturom preko 30 °C, godišnji prośek</figcaption>
  <p class="fig-sub">Poređenje dva standardna tridesetogodišnja razdoblja i posljednjih petnaest godina. Unutrašnjost se zagrijava brže od obale.</p>
  <div class="fig-plot">
    <svg viewBox="0 0 680 300" role="img" width="100%" aria-label="Stubičasti dijagram. Broj dana godišnje sa temperaturom preko 30 stepeni: Budva 13, 31 i 44 dana u razdobljima 1961-1990, 1991-2020 i 2011-2025; Podgorica 18, 43 i 67 dana u istim razdobljima.">
      <line x1="60" y1="250" x2="660" y2="250" stroke="#d1d5da" stroke-width="1"/>
      <line x1="60" y1="193" x2="660" y2="193" stroke="#eef0f2" stroke-width="1"/>
      <line x1="60" y1="136" x2="660" y2="136" stroke="#eef0f2" stroke-width="1"/>
      <line x1="60" y1="79" x2="660" y2="79" stroke="#eef0f2" stroke-width="1"/>
      <text x="52" y="254" text-anchor="end" font-size="11" fill="#6a737d">0</text>
      <text x="52" y="197" text-anchor="end" font-size="11" fill="#6a737d">20</text>
      <text x="52" y="140" text-anchor="end" font-size="11" fill="#6a737d">40</text>
      <text x="52" y="83" text-anchor="end" font-size="11" fill="#6a737d">60</text>

      <rect x="102" y="213" width="54" height="37" rx="3" fill="#0366d6"/>
      <text x="129" y="206" text-anchor="middle" font-size="12" font-weight="600" fill="#24292e">13</text>
      <rect x="164" y="199" width="54" height="51" rx="3" fill="#c2410c"/>
      <text x="191" y="192" text-anchor="middle" font-size="12" font-weight="600" fill="#24292e">18</text>
      <text x="160" y="272" text-anchor="middle" font-size="12" fill="#586069">1961–1990</text>

      <rect x="302" y="161" width="54" height="89" rx="3" fill="#0366d6"/>
      <text x="329" y="154" text-anchor="middle" font-size="12" font-weight="600" fill="#24292e">31</text>
      <rect x="364" y="127" width="54" height="123" rx="3" fill="#c2410c"/>
      <text x="391" y="120" text-anchor="middle" font-size="12" font-weight="600" fill="#24292e">43</text>
      <text x="360" y="272" text-anchor="middle" font-size="12" fill="#586069">1991–2020</text>

      <rect x="502" y="124" width="54" height="126" rx="3" fill="#0366d6"/>
      <text x="529" y="117" text-anchor="middle" font-size="12" font-weight="600" fill="#24292e">44</text>
      <rect x="564" y="59" width="54" height="191" rx="3" fill="#c2410c"/>
      <text x="591" y="52" text-anchor="middle" font-size="12" font-weight="600" fill="#24292e">67</text>
      <text x="560" y="272" text-anchor="middle" font-size="12" fill="#586069">2011–2025</text>

      <rect x="60" y="20" width="12" height="12" rx="2" fill="#0366d6"/>
      <text x="78" y="30" font-size="12" fill="#586069">Budva</text>
      <rect x="140" y="20" width="12" height="12" rx="2" fill="#c2410c"/>
      <text x="158" y="30" font-size="12" fill="#586069">Podgorica</text>
    </svg>
  </div>
  <p class="fig-src">Izvor: ERA5 reanaliza preko Open-Meteo arhive, tačke 42,28° SGŠ 18,84° IGD i 42,44° SGŠ 19,26° IGD. Mreža od oko 9 km miješa more, dolinu i planinu, pa su apsolutne vrijednosti niže nego na stanici, a odnos između razdoblja ostaje valjan.</p>
</figure>

        <h3>Zašto 2030, a ne 2100</h3>
        <p>
            Scenariji emisija se međusobno razilaze tek poslije 2040. Do 2030. je razlika između najambicioznijeg i najgoreg puta manja od dvije desetine stepena, jer sve što će se dogoditi u narednih pet godina već je u okeanu i u atmosferi. WMO za razdoblje 2026–2030. daje 91% izgleda da bar jedna godina privremeno pređe 1,5 °C, 75% da to učini i petogodišnji prośek, i 86% da bar jedna godina obori rekord iz 2024. Raspon godišnjih vrijednosti je od 1,3 do 1,9 °C.
        </p>
        <p>
            Za narednih pet godina, dakle, smanjenje emisija u regionu ne mijenja ovdašnje vrijeme; ono mijenja cijenu izvoza, pristup fondovima i kvalitet vazduha u Pljevljima i Nikšiću. Ono što mijenja ovdašnje vrijeme jeste priprema, a tu se stoji najgore.
        </p>

        <h3>Gdje će se osjetiti</h3>
        <p>
            Voda je prva. Problem nije godišnja količina kiše, koja se do 2030. neće bitno promijeniti, nego raspored i isparavanje: toplije ljeto isuši tlo i akumulacije i kad padne ista kiša. Zapadni Balkan je već u ljeto 2025. uvodio restrikcije, Srbija je proglašavala ekstremnu sušu, a Skadarsko jezero ima trend pada nivoa u kasno ljeto. Uz to, vodovod na primorju gubi između 30 i 45% zahvaćene vode, što je najjeftinija rezerva koju region ima.
        </p>
        <p>
            Struja je druga. Region veliki dio potrošnje pokriva iz hidroelektrana, pa u sušnoj godini proizvodnja pada tačno onda kad potrošnja za hlađenje raste. Albanija je u prvoj polovini 2025. na uvoz struje potrošila oko 60 miliona eura. Procjene za albanske hidroelektrane govore o mogućem padu proizvodnje od 15% u velikim i 20% u malim postrojenjima.
        </p>
        <p>
            Zatim požari, koji su 2026. dali jednu od najgorih evropskih sezona, a Crna Gora je po udjelu izgorjele u ukupnoj teritoriji prošla gore od Španije i Portugala. Pa zdravlje: između 1991. i 2020. toplota je u južnoj Evropi ubijala šest puta više nego u śevernoj, a za zapadni Balkan se projektuje porast smrtnosti povezane sa toplotom od oko 20%. Pa turizam, koji dobija bolji maj, jun, septembar i oktobar, a gubi na udobnosti u julu i avgustu.
        </p>

        <h3>Šta se može uraditi za pet godina</h3>
        <p>
            Svjetska banka procjenjuje da bi klimatske nepogode do 2050. mogle smanjiti crnogorski bruto domaći proizvod za 7,9%. Poplave su najskuplja pojedinačna opasnost: pogađaju oko 10 000 ljudi godišnje i nose prośečno 90 miliona dolara štete. Početni paket prilagođavanja procijenjen je na 5,7 milijardi dolara, sa težištem na mjerama do 2030.
        </p>
        <p>
            Od toga se nekoliko stvari može uraditi bez čekanja na fondove: spustiti gubitke u vodovodu ispod 25%, uvesti sistem ranog upozoravanja na toplotne talase sa protokolom za domove za stare i za rad na otvorenom, i uskladiti propuste i bujične tokove na primorju sa današnjim, a ne sa nekadašnjim intenzitetom padavina. Pet godina je prekratak rok da se promijeni klima, a sasvim dovoljan za vodovod i za propust ispod magistrale.
        </p>
    </div>

'''

EXTRA_SOURCES = (
    '            <li><a href="https://climate.copernicus.eu/ten-charts-discover-european-state-climate-2025-report" target="_blank" rel="noreferrer">Copernicus, European State of the Climate 2025</a></li>\n'
    '            <li><a href="https://wmo.int/resources/publication-series/wmo-global-annual-decadal-climate-update/global-annual-decadal-climate-update-2026-2035" target="_blank" rel="noreferrer">WMO, Global Annual to Decadal Climate Update</a></li>\n'
    '            <li><a href="https://joint-research-centre.ec.europa.eu/jrc-news-and-updates/worsening-drought-and-record-heat-grip-europe-fuelling-extraordinary-wildfires-and-extremely-low-2026-08-12_en" target="_blank" rel="noreferrer">Zajednički istraživački centar, suša, vodostaji i požari u Evropi, avgust 2026.</a></li>\n'
    '            <li><a href="https://www.worldbank.org/en/country/montenegro/publication/montenegro-country-climate-and-development-report" target="_blank" rel="noreferrer">Svjetska banka, izvještaj o klimi i razvoju za Crnu Goru</a></li>\n'
    '            <li><a href="https://www.medecc.org/main-facts/" target="_blank" rel="noreferrer">MedECC, glavni nalazi za Sredozemlje</a></li>\n'
    '            <li><a href="https://open-meteo.com/en/docs/historical-weather-api" target="_blank" rel="noreferrer">ERA5 reanaliza preko Open-Meteo arhive, izračuni za Budvu i Podgoricu</a></li>\n'
)

ANCHOR = '    <div class="article">\n        <h2>Izvori</h2>'
LAST_SOURCE = ('            <li><a href="https://wmo.int/media/news/wmo-likelihood-increases-of-el-nino" '
               'target="_blank" rel="noreferrer">WMO, saopštenja o El Niñu</a></li>\n')


def main():
    page = io.open(PAGE, encoding="utf-8").read()
    if "20_VIII_MMXXVI_balkan_2030.pdf" in page:
        print("članak već postoji, preskačem")
        return
    assert ANCHOR in page
    page = page.replace(ANCHOR, ARTICLE + ANCHOR)
    assert LAST_SOURCE in page
    page = page.replace(LAST_SOURCE, LAST_SOURCE + EXTRA_SOURCES)
    io.open(PAGE, "w", encoding="utf-8").write(page)
    print("upisano:", PAGE)


if __name__ == "__main__":
    main()
