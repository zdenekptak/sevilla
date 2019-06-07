import requests                       # stahuje html stranku
import time                           # vlozi casovou prodlevu
from bs4 import BeautifulSoup         # prelozi stranku do strojove zpracovatelne podoby
from unidecode import unidecode       # prece s diakritikou
import pickle                         # ukladani do souboru
import sys                            # zvysi limit pro rekurze
sys.setrecursionlimit(1000000)        # bez toho nefunguje pickle s nasimi objekty
import smtplib, ssl                   # odesila email
from email.mime.text import MIMEText  # formatovani emailu


class Inzerat:

    def __init__(self, html_blok_div):               # konstruktor (vytváří nový objekt)
        self.html_blok_div = html_blok_div

    def hledani_html_odkazu(self):                   # vyhledavani odkazu
        self.odkaz = self.html_blok_div.a['href']

    def topovany_inzerat(self):                      # rozpoznani topovaneho inzeratu
        if "Topován" in str(self.html_blok_div):
            self.top = True
        else:
            self.top = False

    def nadpis_a_popisek(self):
        # Stahne stranku s vyrobkem a ulozi do promenne "stranka_inzeratu".
        stranka_inzeratu = requests.get(self.odkaz)

        # Vezme celou stranku a pomoci parsovani zpracuje stranku do strojove spracovtelne podoby.
        citelny_html = BeautifulSoup(stranka_inzeratu.content, 'html.parser')

        # Extrahuje prvni "h1" a "p" na html strance.
        self.nadpis = citelny_html.find('h1').get_text()
        self.popisek = citelny_html.find('p').get_text()

    def je_relevantni(self, klicova_slova):                         # najde inzerat podle klicovych slov

        for klicove_slovo in klicova_slova:
            klicove_slovo = unidecode(klicove_slovo)
            if klicove_slovo in unidecode(self.nadpis.lower()) or klicove_slovo in unidecode(self.popisek.lower()):
                return True
        return False

class InzeratDownloader:

    @classmethod
    def stahni_vse(cls, url):
        sbazar = requests.get(url)
        mobile = BeautifulSoup(sbazar.content, 'html.parser')   #upravime stranku do strojove podoby a ulozime do promenne
        bloky_div = mobile.find_all('div', class_='c-item__group')   #Najde vsechny bloky 'div' s inzeratem a vrati pocet

        vsechny_inzeraty = []
        for blok in bloky_div:
            inzerat = Inzerat(blok)
            inzerat.hledani_html_odkazu()
            inzerat.topovany_inzerat()
            inzerat.nadpis_a_popisek()
            vsechny_inzeraty.append(inzerat)
            print(f'Stazen inzerat {inzerat.odkaz}')
            time.sleep(2)

        return vsechny_inzeraty

    @classmethod
    def stahni(cls, url, zname_top_inzeraty, zname_netop_inzeraty):
        sbazar = requests.get(url)
        mobile = BeautifulSoup(sbazar.content, 'html.parser')   #upravime stranku do strojove podoby a ulozime do promenne
        bloky_div = mobile.find_all('div', class_='c-item__group')   #Najde vsechny bloky 'div' s inzeratem a vrati pocet

        nove_top_inzeraty = []
        for blok in bloky_div:
            inzerat = Inzerat(blok)
            inzerat.hledani_html_odkazu()
            inzerat.topovany_inzerat()
            inzerat.nadpis_a_popisek()
            if inzerat.top:
                if inzerat.odkaz == zname_top_inzeraty[0].odkaz:
                    break
                nove_top_inzeraty.append(inzerat)
                print(f'Stazen topovany inzerat {inzerat.nadpis}')
            time.sleep(2)

        nove_netop_inzeraty = []
        for blok in bloky_div:
            inzerat = Inzerat(blok)
            inzerat.hledani_html_odkazu()
            inzerat.topovany_inzerat()
            inzerat.nadpis_a_popisek()
            if not inzerat.top:
                if inzerat.odkaz == zname_netop_inzeraty[0].odkaz:
                    break
                nove_netop_inzeraty.append(inzerat)
                print(f'Stazen netopovany inzerat {inzerat.nadpis}')
            time.sleep(2)

        return nove_top_inzeraty + nove_netop_inzeraty

class InzeratLoader:

    def nacti_top(jmeno_souboru):
        zname_top_inzeraty = pickle.load(open(jmeno_souboru, "rb"))
        print('Nacteno', len(zname_top_inzeraty), 'topovanych inzeratu z disku')
        print(f'Prvni nacteny topovany inzerat z disku:  {zname_top_inzeraty[0].nadpis}')
        return zname_top_inzeraty

    def nacti_netop(jmeno_souboru):
        zname_netop_inzeraty = pickle.load(open(jmeno_souboru, "rb"))
        print('Nacteno', len(zname_netop_inzeraty), 'netopovanych inzeratu z disku')
        print(f'Prvni nacteny netopovany inzerat z disku:  {zname_netop_inzeraty[0].nadpis}')
        return zname_netop_inzeraty

class KeywordLoader:

    def nacti_klicova_slova(soubor_klic_slov):
        klic_slova = open(soubor_klic_slov, "r")
        seznam_klic_slov = []
        for klic_slovo in klic_slova:
            seznam_klic_slov.append(klic_slovo.strip())
        return seznam_klic_slov

class InzeratSplitter:

    def topovane_inzeraty(inzeraty):
        topovane_inzeraty = []
        for x in inzeraty:
            if x.top:
                topovane_inzeraty.append(x)
        print(f'Nalezeno {len(topovane_inzeraty)} topovanych inzeratu')
        return topovane_inzeraty

    def netopovane_inzeraty(inzeraty):
        netopovane_inzeraty = []
        for y in inzeraty:
            if not y.top:
                netopovane_inzeraty.append(y)
        print(f'Nalezeno {len(netopovane_inzeraty)} netopovanych inzeratu')
        return netopovane_inzeraty

class InzeratSaver:

    def uloz_top_inzerat(inzeraty, jmeno_souboru):
        if len(inzeraty) > 0:
            pickle.dump(inzeraty, open(jmeno_souboru, "wb"))
            print(f'Ulozeno {len(inzeraty)} topovanych inzeratu')

    def uloz_netop_inzerat(inzeraty, jmeno_souboru):
        if len(inzeraty) > 0:
            pickle.dump(inzeraty, open(jmeno_souboru, "wb"))
            print(f'Ulozeno {len(inzeraty)} netopovanych inzeratu')

class MailSender:

    def posliemail(inzeraty_k_odeslani, posta_nazev_souboru):

        # otevreni souboru
        posta_soubor = open(posta_nazev_souboru, 'r')

        # nacitani prijemce ze souboru
        prijemce = posta_soubor.readline().strip()

        # nacteni odesilatele ze souboru
        odesilatel = posta_soubor.readline().strip()

        # nacteni hesla ze souboru
        password = posta_soubor.readline().strip()

        # Create the plain-text and HTML version of your message
        html = "<html><body>"
        for i in inzeraty_k_odeslani:
            html += f"<h1>{i.nadpis}</h1>"
            html += f"<p>{i.popisek}</p>"
            html += f'<a href="{i.odkaz}">{i.odkaz}</a>'
        html += "</body></html>"

        message = MIMEText(html, "html")
        message["Subject"] = "Inzerat SBAZAR"
        message["From"] = odesilatel
        message["To"] = prijemce

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(odesilatel, password)
            server.sendmail(
                odesilatel, prijemce, message.as_string()
            )

        print(f'Pocet odeslanych inzeratu: {len(inzeraty_k_odeslani)}')

    
