# Budva Weather Forecast — ML korekcija prognoze

Korigovana 48-satna i 7-dnevna prognoza za Budvu. Pipeline preuzima sirove
prognoze sa 11 globalnih NWP modela, uči njihov bias na 6 godina lokalnih
mjerenja i objavljuje JSON koji pokreće web stranicu.

## Kako radi

1. **Historijski podaci** — satne prognoze (2020–2026) sa Open-Meteo API-ja,
   uparene sa mjerenjima sa [IBUDVA5](https://www.wunderground.com/dashboard/pws/IBUDVA5)
   Weather Underground stanice.
2. **Trening** — XGBoost, CatBoost i LightGBM uče bias svakog NWP modela za
   temperaturu, vlažnost, vjetar, pritisak, oblačnost i padavine; Ridge
   stacking kombinuje korekcije. Za padavine: focal loss, izotonička
   kalibracija i precision-first prag, uz kvantilne modele (CQR) za
   distribucionu prognozu.
3. **Live prognoza** — GitHub Actions pokreće pipeline na svakih 5 sati
   (`--skip-training`): preuzme najnovije prognoze, primijeni korekciju i
   generiše `forecast_48h.json`. SKALA radar nowcast (poseban budva-radar
   projekat) blenduje se u prvih nekoliko sati padavina.
4. **Narativ** — dnevni opis generiše pravilo-bazirani generator; Gemini ga
   samo prefrazira, a deterministički guardrail (`gemini_narrative.validate`)
   odbacuje svaku halucinaciju i vraća sigurnu rečenicu.
5. **Web prikaz** — statična stranica (`docs/forecast.html`) čita JSON i
   prikazuje kartice, grafikone, marine prognozu i radar status.

## Modeli

| Model | Rezolucija |
|-------|-----------|
| ARPÈGE Europe | ~10 km |
| GFS Seamless | ~25 km |
| ICON Seamless | ~13 km |
| Météo-France | ~10 km |
| ECMWF IFS 0.25° | ~25 km |
| ItaliaMeteo ICON-2I | ~2.2 km |
| UKMO Seamless | ~10 km |
| BOM ACCESS | ~12 km |
| ECMWF IFS | ~9 km |
| KNMI Seamless | ~11 km |
| DMI Seamless | ~13 km |

## Struktura

```
forecast_48h_v3.py          # Glavni pipeline (fetch → train → correct → output)
prob_forecast.py            # Probabilistički alati (EMOS, CQR, ECC, verifikacija)
gemini_narrative.py         # Gemini prefraziranje + guardrail
narrative_variants.py       # Pool fraza za dnevni narativ
wu_scraper.py               # Scraper historijskih obs (Weather Underground)
advanced_model_analysis.py  # Analiza grešaka po modelu
visualize_analysis*.py      # Grafikoni analize
trained_models_v2/          # Trenirani modeli + bias tabele
.github/workflows/
  forecast.yml              # Cron na svakih 5 sati
docs/
  forecast.html             # 48h + 7-dnevna prognoza
  index.html                # Analiza tačnosti modela
  forecast_data/forecast_48h.json
```

## Pokretanje

```bash
pip install -r requirements.txt

python forecast_48h_v3.py                  # puni pipeline (trening + prognoza)
python forecast_48h_v3.py --skip-training  # samo prognoza, postojeći modeli

python test_gemini_narrative.py            # testovi guardrail-a
python test_narrative_variants.py

node test_nowcast_hourly.js                # SKALA NOWCAST gating u docs/forecast.html
```

Output ide u `forecast_output/forecast_48h.json`; GitHub Actions ga kopira u
`docs/forecast_data/`. Gemini narativ traži `GEMINI_API_KEY` u okruženju;
bez ključa pipeline koristi pravilo-bazirane rečenice.

## Šansa za padavine

`precip_probability` na dnevnoj kartici je procenat NWP modela (od 11) koji
predviđaju >0.1 mm u bilo kom satu tog dana — consensus metrika. Satna
kalibrisana PoP (izotonička kalibracija + prag) i kvantilna traka postoje
kao poseban sloj u JSON-u kad su modeli trenirani.

## Autor

Matija Ivanović · [@matko-iv](https://github.com/matko-iv)
