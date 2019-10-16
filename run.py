from inzerat_handlers import Inzerat, InzeratLoader, InzeratDownloader, InzeratSplitter, InzeratSaver, KeywordLoader, MailSender


jmeno_souboru_top = "seznam_inzeratu_topovane.pkl"
jmeno_souboru_netop = "seznam_inzeratu_netopovane.pkl"
config = "config.json"
min_ulozenych_inz = 10

inzeraty_z_disku_top = InzeratLoader.nacti_top(jmeno_souboru_top)
inzeraty_z_disku_netop = InzeratLoader.nacti_netop(jmeno_souboru_netop)

nove_inzeraty = InzeratDownloader.stahni(config, inzeraty_z_disku_top, inzeraty_z_disku_netop)

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


klicova_slova = KeywordLoader.nacti_klicova_slova(config)

inzeraty_roztridene_podle_klic_slov = []
for x in nove_inzeraty:
    if x.je_relevantni(klicova_slova):
        inzeraty_roztridene_podle_klic_slov.append(x)

if len(inzeraty_roztridene_podle_klic_slov) > 0:
    MailSender.posliemail(inzeraty_roztridene_podle_klic_slov, config)
else:
    print("Nebyly nalezeny žádné odpovídající inzeráty")
