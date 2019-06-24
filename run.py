jmeno_souboru_top = "seznam_inzeratu_topovane.pkl"
jmeno_souboru_netop = "seznam_inzeratu_netopovane.pkl"
URL = "https://www.sbazar.cz/94-mobil-bazar/praha?radius=50"
seznam_klic_slov = "klicovaslova.txt"
prijemce = "posta.txt"
min_ulozenych_inz = 10


inzeraty_z_disku_top = InzeratLoader.nacti_top(jmeno_souboru_top)
inzeraty_z_disku_netop = InzeratLoader.nacti_netop(jmeno_souboru_netop)

nove_inzeraty = InzeratDownloader.stahni(URL, inzeraty_z_disku_top, inzeraty_z_disku_netop)

rozdelene_inzeraty_top = InzeratSplitter.topovane_inzeraty(nove_inzeraty)
rozdelene_inzeraty_netop = InzeratSplitter.netopovane_inzeraty(nove_inzeraty)

# Doplnění na minimalni počet inzerátů top pro uložení
ukladane_top_inzeraty = rozdelene_inzeraty_top
if len(ukladane_top_inzeraty) < min_ulozenych_inz:
    pocet_top_doplneni = min_ulozenych_inz - len(ukladane_top_inzeraty)
    ukladane_top_inzeraty += inzeraty_z_disku_top[0:pocet_top_doplneni]

# Doplnění na minimalni počet inzerátů netop pro uložení
ukladane_netop_inzeraty = rozdelene_inzeraty_netop
if len(ukladane_netop_inzeraty) < min_ulozenych_inz:
    pocet_netop_doplneni = min_ulozenych_inz - len(ukladane_netop_inzeraty)
    ukladane_netop_inzeraty += inzeraty_z_disku_netop[0:pocet_netop_doplneni]


InzeratSaver.uloz_top_inzerat(ukladane_top_inzeraty, jmeno_souboru_top)
InzeratSaver.uloz_netop_inzerat(ukladane_netop_inzeraty, jmeno_souboru_netop)

klicova_slova = KeywordLoader.nacti_klicova_slova(seznam_klic_slov)

bastakovy_inzeraty= []
for x in nove_inzeraty:
    if x.je_relevantni(klicova_slova):
        bastakovy_inzeraty.append(x)

if len(bastakovy_inzeraty) > 0:
    MailSender.posliemail(bastakovy_inzeraty, prijemce)

else:
    print("Nebyly nalezeny žádné odpovídající inzeráty")

