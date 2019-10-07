import requests                       # stahuje html stranku
import time                           # vlozi casovou prodlevu
from bs4 import BeautifulSoup         # prelozi stranku do strojove zpracovatelne podoby
from unidecode import unidecode       # prece s diakritikou
import pickle                         # ukladani do souboru
import sys                            # zvysi limit pro rekurze
sys.setrecursionlimit(1000000)        # bez toho nefunguje pickle s nasimi objekty
import smtplib, ssl                   # odesila email
from email.mime.text import MIMEText  # formatovani emailu
import json


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

    def nacteni_detailu(self):
        # Stahne stranku s vyrobkem a ulozi do promenne "stranka_inzeratu".
        stranka_inzeratu = requests.get(self.odkaz)

        # Vezme celou stranku a pomoci parsovani zpracuje stranku do strojove spracovtelne podoby.
        citelny_html = BeautifulSoup(stranka_inzeratu.content, 'html.parser')

        # Extrahuje prvni "h1" a "p" na html strance.
        self.nadpis = citelny_html.find('h1').get_text()
        self.popisek = citelny_html.find('p').get_text()
        self.cena = citelny_html.find('b', class_='c-price__price').get_text()

    def je_relevantni(self, klicova_slova):                         # najde inzerat podle klicovych slov

        for klicove_slovo in klicova_slova:
            klicove_slovo = unidecode(klicove_slovo)
            if klicove_slovo in unidecode(self.nadpis.lower()) or klicove_slovo in unidecode(self.popisek.lower()):
                return True
        return False

class InzeratDownloader:

    @classmethod
    def stahni(cls, config_soubor, zname_top_inzeraty, zname_netop_inzeraty):
        with open(config_soubor) as json_file:
            config = json.load(json_file)
            url = config["url"]

        sbazar = requests.get(url)
        mobile = BeautifulSoup(sbazar.content, 'html.parser')   #upravime stranku do strojove podoby a ulozime do promenne
        bloky_div = mobile.find_all('div', class_='c-item__group')   #Najde vsechny bloky 'div' s inzeratem a vrati pocet

        nove_top_inzeraty = []
        for blok in bloky_div:
            inzerat = Inzerat(blok)
            inzerat.hledani_html_odkazu()
            inzerat.topovany_inzerat()
            inzerat.nacteni_detailu()

            if inzerat.top:
                ulozene_top_odkazy = []
                for znamy_top_odkaz in zname_top_inzeraty:
                    ulozene_top_odkazy.append(znamy_top_odkaz.odkaz)
                if inzerat.odkaz in ulozene_top_odkazy:
                    break

                nove_top_inzeraty.append(inzerat)
                print(f'Stazen topovany inzerat {inzerat.nadpis}')
            time.sleep(2)

        nove_netop_inzeraty = []
        for blok in bloky_div:
            inzerat = Inzerat(blok)
            inzerat.hledani_html_odkazu()
            inzerat.topovany_inzerat()
            inzerat.nacteni_detailu()
            if not inzerat.top:
                ulozene_netop_inzeraty = []
                for znamy_netop_odkaz in zname_netop_inzeraty:
                    ulozene_netop_inzeraty.append(znamy_netop_odkaz.odkaz)
                if inzerat.odkaz in ulozene_netop_inzeraty:
                    break

                nove_netop_inzeraty.append(inzerat)
                print(f'Stazen netopovany inzerat {inzerat.nadpis}')
            time.sleep(2)

        return nove_top_inzeraty + nove_netop_inzeraty

class InzeratLoader:

    def nacti_top(jmeno_souboru):
        try:
                zname_top_inzeraty = pickle.load(open(jmeno_souboru, 'rb'))
                print('Nacteno', len(zname_top_inzeraty), 'topovanych inzeratu z disku')
                print(f'Prvni nacteny topovany inzerat z disku:  {zname_top_inzeraty[0].nadpis}')
        except FileNotFoundError:
                zname_top_inzeraty = []
                print('Nebyl nalezen soubor se znamymi topovanymi inzeraty')
                print('Pokracuji dale s prazdnym seznamem')
        return zname_top_inzeraty

    def nacti_netop(jmeno_souboru):
        try:
                zname_netop_inzeraty = pickle.load(open(jmeno_souboru, 'rb'))
                print('Nacteno', len(zname_netop_inzeraty), 'netopovanych inzeratu z disku')
                print(f'Prvni nacteny netopovany inzerat z disku:  {zname_netop_inzeraty[0].nadpis}')
        except FileNotFoundError:
                zname_netop_inzeraty = []
                print('Nebyl nalezen soubor se znamymi netopovanymi inzeraty')
                print('Pokracuji dale s prazdnym seznamem')
        return zname_netop_inzeraty


class KeywordLoader:

    def nacti_klicova_slova(config_soubor):

        with open(config_soubor) as json_file:

            config = json.load(json_file)
            klic_slova = config["keywords"]
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

    def posliemail(inzeraty_k_odeslani, config_soubor):

        # otevreni souboru
        with open(config_soubor) as json_file:

            config = json.load(json_file)

            prijemce = config["prijemce"]
            odesilatel = config["odesilatel"]
            password = config["heslo"]
            smtp = config["smtp_server"]
            smtp_port = config["smtp_port"]

        # Create the plain-text and HTML version of your message
        html = "<html><body>"
        for i in inzeraty_k_odeslani:
            html += f"<h1>{i.nadpis}</h1>"
            html += f"<p>{i.popisek}</p>"
            html += f"<b>{i.cena} Kč</b><br />"
            html += f'<a href="{i.odkaz}">{i.odkaz}</a>'
        html += "</body></html>"

        message = MIMEText(html, "html")
        message["Subject"] = "Inzerat SBAZAR"
        message["From"] = odesilatel
        message["To"] = prijemce

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp, smtp_port, context=context) as server:  #smtp.gmail.com smtp-140148.m48.wedos.net
            server.login(odesilatel, password)
            server.sendmail(
                odesilatel, prijemce, message.as_string()
            )

        print(f'Pocet odeslanych inzeratu: {len(inzeraty_k_odeslani)}')
