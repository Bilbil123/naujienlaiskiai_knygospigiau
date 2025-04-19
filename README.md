# Knygospigiau.lt Naujienlaiškių Sistema

Programa skirta kurti ir siųsti naujienlaiškius Knygospigiau.lt klientams.

## Funkcijos

- Šventinių akcijų šablonai
- Teksto formatavimas (šriftai, dydžiai, spalvos)
- Emojių įterpimas
- Nuorodų valdymas
- HTML laiškų kūrimas
- Automatinis siuntimas visiems prenumeratoriams

## Reikalavimai

- Python 3.11 arba naujesnė versija
- PyQt5
- Kiti reikalavimai nurodyti requirements.txt faile

## Diegimas

1. Klonuokite repozitoriją:
```bash
git clone https://github.com/JUSU_USERNAME/naujienlaiskiai_knygospigiau.git
cd naujienlaiskiai_knygospigiau
```

2. Sukurkite virtualią aplinką:
```bash
python -m venv venv
source venv/bin/activate  # Unix/macOS
# ARBA
.\venv\Scripts\activate  # Windows
```

3. Įdiekite reikalingus paketus:
```bash
pip install -r requirements.txt
```

4. Sukurkite `email_list.txt` failą su gavėjų el. pašto adresais (po vieną eilutėje)

5. Paleiskite programą:
```bash
python email_sender_app.py
```

## Programos sukūrimas

Norėdami sukurti vykdomąjį failą:

```bash
pyinstaller --clean --windowed --name "Knygospigiau Newsletter" --add-data "email_sender_ui.py:." --add-data "send_emails.py:." --hidden-import PyQt5.QtCore --hidden-import PyQt5.QtWidgets --hidden-import send_emails --hidden-import email_sender_ui email_sender_app.py
```

## Naudojimas

1. Paleiskite programą
2. Įveskite laiško antraštę
3. Pasirinkite šventinę akciją arba sukurkite savo tekstą
4. Suformatuokite tekstą naudodami teksto formatavimo įrankius
5. Įterpkite emojius ir nuorodas pagal poreikį
6. Spauskite "Siųsti laiškus" kai laiškas paruoštas

## Licencija

Šis projektas yra privatus ir skirtas tik Knygospigiau.lt naudojimui. 