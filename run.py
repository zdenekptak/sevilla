from handlers import inzerat_handlers

jmeno_souboru_top = "seznam_inzeratu_topovane.pkl"
jmeno_souboru_netop = "seznam_inzeratu_netopovane.pkl"
URL = "https://www.sbazar.cz/94-mobil-bazar/praha?radius=50"
seznam_klic_slov = "klicovaslova.txt"

inzeraty_z_disku_top = InzeratLoader.nacti_top(jmeno_souboru_top)
inzeraty_z_disku_netop = InzeratLoader.nacti_netop(jmeno_souboru_netop)

inzeraty = InzeratDownloader.stahni(URL, inzeraty_z_disku_top, inzeraty_z_disku_netop)

rozdelene_inzeraty_top = InzeratSplitter.topovane_inzeraty(inzeraty)
rozdelene_inzeraty_netop = InzeratSplitter.netopovane_inzeraty(inzeraty)

InzeratSaver.uloz_top_inzerat(rozdelene_inzeraty_top, jmeno_souboru_top)
InzeratSaver.uloz_netop_inzerat(rozdelene_inzeraty_netop, jmeno_souboru_netop)

klicova_slova = KeywordLoader.nacti_klicova_slova(seznam_klic_slov)

bastakovy_inzeraty= []
for x in inzeraty:
    if x.je_relevantni(klicova_slova):
        bastakovy_inzeraty.append(x)

if len(bastakovy_inzeraty) > 0:
    MailSender.posliemail(bastakovy_inzeraty)
