# coding=UTF-8

# brakujące:
# ur.krakow.pl -> brak wystawionego API
# aps.edu.pl -> brak wystawionego API
# po.edu.pl -> brak wystawionego API
# up.wroc.pl -> brak wystaionego API
# prawowroclaw.edu.pl -> brak wystawionego API
# wsb.net.pl -> brak wystawionego API
# ajd.czest.pl -> brak wystawionego API

USOSINSTANCES = [
    {'usos_id': 'UW',
     'name': 'Uniwersytet Warszawski',
     'url': 'https://usosapps.uw.edu.pl/',
     'logo': '/static/img/logo/logo-uw-64x64.jpg',
     'consumer_key': 'KBt6uWPWUekUzFtNTyY9',                         # jeszcze stary nie zmieniony na Kujon.mobi
     'consumer_secret': 'Bm7wwuKSekhZKFs77GmP4vxHKgf4B7nFmSzUfWeG',  # jeszcze stary nie zmieniony na Kujon.mobi
     'contact': 'dsksysadm@adm.uw.edu.pl',
     'enabled': True,
    },
    {'usos_id': 'UJ',                           #fiuty zablokowali dostep dla zewnetrznych aplikacji
     'name': 'Uniwersytet Jagieloński w Krakowie',
     'url': 'https://apps.usos.uj.edu.pl/',
     'logo': '/static/img/logo/logo-uj-64x64.jpg',
     'consumer_key': 'QbYhMjzfXUmZr77nQ2KM',
     'consumer_secret': 'rhJnuea4gPbqHJSw5Qy2JFwjeP3ZmyhtwhwTeWtm',
     'contact': 'michal.pysz@uj.edu.pl, michal.zabicki@uj.edu.pl',
     'enabled': False,
    },
    {'usos_id': 'UAM',
     'name': 'Uniwersytet im Adama Mickiewicza w Poznaniu',
     'url': 'https://usosapps.amu.edu.pl/',
     'logo': '/static/img/logo/logo-uam-64x64.jpg',
     'consumer_key': 'aUvvxdTH9kLj7VqNxqcy',
     'consumer_secret': 'RSE9tqZpEdzqQxjQBVvqxJPCjy44e6JDY6LtZ3HH',
     'contact': 'd.walczyk@tu.kielce.pl',
     'enabled': True,
    },
    {'usos_id': 'PW',
     'name': 'Politechnika Warszawska',
     'url': 'https://apps.usos.pw.edu.pl/',
     'logo': '/static/img/logo/logo-pw-64x64.jpg',
     'consumer_key': 'uc9khJyJemwKh6pULnJ8',
     'consumer_secret': 'RJDpj7RYK7u84R5BrUuSMuAz8fspHK3SLts7JUKV',
     'contact': 'usos-support@ci.pw.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'UL',
     'name': 'Uniwersytet Łódzki',
     'url': 'https://usosapps.uni.lodz.pl/',
     'logo': '/static/img/logo/logo-ul-64x64.jpg',
     'consumer_key': 'e2ZkgjZUQsuB4NwUa9gC',
     'consumer_secret': 'eXdAH75VsTd3wSu7bsEzgE7hKnzmWmMWqWajFgq7',
     'contact': 'mariusz.ruszkowski@uni.lodz.pl, pawel.dziuba@uni.lodz.pl, konrad.maksymowicz@uni.lodz.pl, dso-logi@uni.lodz.pl, karol.kornatka@uni.lodz.pl',
     'enabled': True,
     },
    {'usos_id': 'UMK',
     'name': 'Uniwersytet Mikołaja Kopernika w Toruniu',
     'url': 'https://usosapps.umk.pl/',
     'logo': '/static/img/logo/logo-umk-64x64.jpg',
     'consumer_key': 'RpkKaKR9kgeRMnwvHR2v',
     'consumer_secret': 'pbuam8sQyU4KCVz5MhJxgPDhJ5J3tj5kKzDC3E3r',
     'contact': 'grusia@umk.pl, piotr@umk.pl, marekcz@umk.pl, efa@umk.pl',
     'enabled': True,
     },
    {'usos_id': 'UWR',
     'name': 'Uniwersytet Wrocławski',
     'url': 'https://usosapps.uni.wroc.pl/',
     'logo': '/static/img/logo/logo-uwr-64x64.jpg',
     'consumer_key': '4Gk554QSht8mwEFPHPRj',
     'consumer_secret': 'QMEhdNBNhe2EA8rUtRKcwAZNUsrUBFPTJETCnZyA',
     'contact': 'pawel@uni.wroc.pl, tomasz.mielnik@uwr.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'US',
     'name': 'Uniwersytet Śląski w Katowicach',
     'url': 'https://usosapps.us.edu.pl/',
     'logo': '/static/img/logo/logo-us-64x64.jpg',
     'consumer_key': 'wJ64nBC9QszCtcWbMhZ2',
     'consumer_secret': 'LUUcUspRZBd5cxqRSaU2JgUsL2WgEwetVjEyw38J',
     'contact': 'mateusz.falfus@us.edu.pl, lukasz.wachstiel@us.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'UMCS',
     'name': 'Uniwersytet Marii Curie-Skłodowskiej w Lublinie',
     'url': 'https://apps.umcs.pl',
     'logo': '/static/img/logo/logo-umcs-64x64.jpg',
     'consumer_key': 'M9ZfkBFrrRULYfKEJJSr',
     'consumer_secret': 'zApXh56mZ42wDz7fSTSKQUX5fqtaUfxP6mEw8Yrd',
     'contact': 'usosweb@umcs.pl',
     'enabled': True,
     },
    {'usos_id': 'UWM',
     'name': 'Uniwersytet Wamińsko-Mazurski w Olsztynie',
     'url': 'https://apps.uwm.edu.pl/',
     'logo': '/static/img/logo/logo-uwm-64x64.jpg',
     'consumer_key': 'Xbrfgb8C43tPpW5tYqf8',
     'consumer_secret': 'pNe6CvRh3rSXY4maD3LSzxyVKJELCHw55K2LhFRU',
     'contact': 'krzysztof.pawliczuk@uwm.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'UKSW',
     'name': 'Uniwersytet Kardynała Stefana Wyszyńskiego',
     'url': 'https://apps.usos.uksw.edu.pl/',
     'logo': '/static/img/logo/logo-uksw-64x64.jpg',
     'consumer_key': 'qbf7G7SUTpd7ygkCCp9q',
     'consumer_secret': '2RwFA9Qs3MVB86eAkgPXHZJ6pmMTrnL69r8TKFZV',
     'contact': 'auto.aos@csi.uksw.edu.pl',
     'enabled': True
     },
    {'usos_id': 'SGH',  # z palca dodane, brak danych!
     'name': 'Szkoła Głowna Handlowa w Warszawie',
     'url': 'https://usosapps.sgh.waw.pl/',
     'logo': '/static/img/logo/logo-sgh-64x64.jpg',
     'consumer_key': 'vAXFTsZvz4RE5ycnVfLy',
     'consumer_secret': 'hYNC27dxWP9Ka74gXxAcUJuC97mLMNza5FSdwDwm',
     'contact': 'usosadmin@sgh.waw.pl, jinowol@sgh.waw.pl',
     'enabled': False
     },
    {'usos_id': 'UP',                   # z palca dodane, przy logowaniu wyświetla błąd Invalid signature
     'name': 'Uniwersytet Przyrodniczy we Wrocławiu',
     'url': 'https://usosapps.up.wroc.pl/',
     'logo': '/static/img/logo/logo-up-64x64.jpg',
     'consumer_key': 'rc3EFkbrSaTKD8fVbTPC',
     'consumer_secret': 'z8ywNGmCYNdYB9JDHU6EAH2HSGgXebLZkytWGAcN',
     'contact': 'usos@up.wroc.pl',
     'enabled': False,
     'disable_ssl_certificate_validation': True
     },
    {'usos_id': 'PRZ',
     'name': 'Politechnika Rzeszowska',
     'url': 'https://usosapps.prz.edu.pl/',
     'logo': '/static/img/logo/logo-prz-64x64.jpg',
     'consumer_key': 'j39vtKXfEPfp3uSDRASf',
     'consumer_secret': 'XcKPVRzyZ94rr7GyPpaNn4Ez63tebuhpNvUX32V7',
     'contact': 'rafim@prz.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'PB',
     'name': 'Politechnika Białostocka',
     'url': 'https://api.uci.pb.edu.pl/',
     'logo': '/static/img/logo/logo-pb-64x64.jpg',
     'consumer_key': 'UEhjUF2Xwxg8P4rzV7Sd',
     'consumer_secret': 'VA4GtQau63yBTzEhBSmb7JX2udkPXta9KtZ68u8R',
     'contact': 'r.klim@uci.pb.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'PS',
     'name': 'Politechnika Świętokrzystka w Kielcach',
     'url': 'https://api.usos.tu.kielce.pl/',
     'logo': '/static/img/logo/logo-ps-64x64.jpg',
     'consumer_key': 'eu75vbGx9BAdcxk3fNdZ',
     'consumer_secret': 'a4eLXfkFx3E2xTzwEPzXcNkCeE3U4SM49DTsQDk6',
     'contact': 'd.walczyk@tu.kielce.pl',
     'enabled': True,
     },
    {'usos_id': 'UKW',
     'name': 'Uniwersytet Kazimierza Wielkiego w Bydgoszczy',
     'url': 'https://api.ukw.edu.pl/',
     'logo': '/static/img/logo/logo-ukw-64x64.jpg',
     'consumer_key': 'essQMkm2VEN6rGdsaq6h',
     'consumer_secret': 'kYe8DVCpxctHMEZKtgmMpXVUV2tf2jjMgqGjUhtF',
     'contact': 'marekmac@ukw.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'WAT',
     'name': 'Wojskowa Akademia Techniczna w Warszawie',
     'url': 'https://usosapps.wat.edu.pl/',
     'logo': '/static/img/logo/logo-wat-64x64.jpg',
     'consumer_key': '9XMbtXUkAJRRU52W5pNA',
     'consumer_secret': 'G5kCRabYSQxnxWLQKhVeuYWxezU4kPPdwvKB2X6B',
     'contact': 'usos@wat.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'UWB',
     'name': 'Uniwersytet Białostocki',
     'url': 'https://usosapps.uwb.edu.pl/',
     'logo': '/static/img/logo/logo-ub-64x64.jpg',
     'consumer_key': 'jf7zsy4F2679RxnpD5v2',
     'consumer_secret': 'gZBkW3GfsNR772acbJm7MB3RVUKGXRYP6e9an4LR',
     'contact': 'usosweb@uwb.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'UO',
     'name': 'Uniwersytet Opolski',
     'url': 'https://usosapps.uni.opole.pl/',
     'logo': '/static/img/logo/logo-uo-64x64.jpg',
     'consumer_key': '3aKC4LkzLgYFf2naByVE',
     'consumer_secret': 'mtQNGUhLyDYPqnWCE75Eyv3J2BJBjgFv5rZK5DU2',
     'contact': 'paszczus@uni.opole.pl, abuhl@uni.opole.pl',
     'enabled': True,
     },
    {'usos_id': 'UTP',
     'name': 'Uniwersytet Technologiczno-Przyrodniczy w Bydgoszczy',
     'url': 'https://usosapps.utp.edu.pl/',
     'logo': '/static/img/logo/logo-utp-64x64.jpg',
     'consumer_key': 'rBERUVJHqqxuNFzzxzvs',
     'consumer_secret': 'hgY9Z8R3FCzCW2yZK4E53XxdpAzRvLgSnmLuszZN',
     'contact': 'usosapps@utp.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'UEW',
     'name': 'Uniwersytet Ekonomiczny we Wrocławiu',
     'url': 'https://usosapps.ue.wroc.pl/',
     'logo': '/static/img/logo/logo-uew-64x64.jpg',
     'consumer_key': '9bqHqt4bEAMUtRmC5tCr',
     'consumer_secret': '2rd8tez3ELXbsq9FvZpdkrRdgvN8aMSk2MF48mtE',
     'contact': 'borys.pogorelo@ue.wroc.pl',
     'enabled': True,
     },
    {'usos_id': 'AWFKAT',
     'name': 'Akademia Wychowania Fizycznego w Katowicach',
     'url': 'https://usosapps.awf.katowice.pl/',
     'logo': '/static/img/logo/logo-awfkat-64x64.jpg',
     'consumer_key': 'QdKazkhftM2Zj2CBXeYB',
     'consumer_secret': 'mSMbUrdHKXq9RA8NKcz5ZPUQZ932UW9bKPV7wek3',
     'contact': 's.kwiatkowski@awf.katowice.pl, b.czerwinski@awf.katowice.pl',
     'enabled': True,
     'disable_ssl_certificate_validation': True
     },
    {'usos_id': 'CHAT',  # z palca dodane
     'name': 'Chrześcijańska Akademia Teologiczna w Warszawie',
     'url': 'https://usosapps.chat.edu.pl/',
     'logo': '/static/img/logo/logo-chat-64x64.jpg',
     'consumer_key': 'uvCDxnLu9L535GM4XDZh',
     'consumer_secret': 'QsPJx6cHAanqxyvBugKubvLdcshJkSqwyaHkh4UW',
     'contact': 'm.frica@chat.edu.pl',
     'enabled': True
     },
    {'usos_id': 'PWSZ-Kalisz',
     'name': 'Państwowa Wyższa Szkoła Zawodowa w Kaliszu',
     'url': 'https://apps.pwsz.kalisz.pl/',
     'logo': '/static/img/logo/logo-pwsz-kalisz-64x64.jpg',
     'consumer_key': 'CYKqXGzT2jwpHQqbRjKJ',
     'consumer_secret': '8rCBFP4M3Lh6Rq6nRudEGP9ywXwnDwyvLh95gCFg',
     'contact': 'wdrozenia@usos.edu.pl',
     'enabled': True
     },
    {'usos_id': 'PWSZ-Krosno',
     'name': 'Państwowa Wyższa Szkoła Zawodowa w Krośnie',
     'url': 'https://usosapps.pwsz.krosno.pl/',
     'logo': '/static/img/logo/logo-pwsz-krosno-64x64.jpg',
     'consumer_key': 'kNBmFG6vvEN6kN265qwB',
     'consumer_secret': 'hMrSp9F7cR2HKqc9e8c7zUeEQHVSTCrQwJUExwZZ',
     'contact': 'mateusz.lorenc@pwsz.krosno.pl',
     'enabled': True
     },
    {'usos_id': 'UTH',
     'name': 'Uczelnia Techniczno-Handlowa w Warszawie',
     'url': 'https://usosapps.uth.edu.pl/',
     'logo': '/static/img/logo/logo-uth-64x64.jpg',
     'consumer_key': 'W4tRcJzT6HFcHAeC7vfc',
     'consumer_secret': 'd8sv6ASBDYbJwqvADSadRHKpAzads6vhxecAGpTn',
     'contact': 'it@uth.edu.pl, luk@wybcz.pl',
     'enabled': True,
     },
    {'usos_id': 'WSE',
     'name': 'Wyższa Szkoła Ekonomiczna w Białymstoku',
     'url': 'https://usosapps.wse.edu.pl/',
     'logo': '/static/img/logo/logo-wse-64x64.jpg',
     'consumer_key': 'WzynWZFyEYPbnxndt9hw',
     'consumer_secret': 'vXNnptJNrc4wGFSvmsteyZeVRV3AKGsDnsNbSRjV',
     'contact': 'usosweb@wse.edu.pl',
     'enabled': True
     },
    {'usos_id': 'PWSIP',
     'name': 'Państwowa Wyższa Szkoła Informatyki i Przedsiębiorczości w Łomży',
     'url': 'https://api.pwsip.edu.pl/usosapps/',
     'logo': '/static/img/logo/logo-pwsip-64x64.jpg',
     'consumer_key': 'ydYepCBkkcPRNzFcaEAp',
     'consumer_secret': 'QHw8B3dYYM5fvbXQRK8xQQbNBLGLY3gMrEAG2Z7P',
     'contact': 'mdabrowski@pwsip.edu.pl',
     'enabled': True
     },
    {'usos_id': 'PWSZ-Elblag',
     'name': 'Państwowa Wyższa Szkoła Zawodowa w Elblągu',
     'url': 'https://usosapps.pwsz.elblag.pl/',
     'logo': '/static/img/logo/logo-pwsz-elblag-64x64.jpg',
     'consumer_key': '7eUrXU8cytknXXKQSgJj',
     'consumer_secret': 'DB7HGw4EvNsUU9nwUE3jrLPfFTHw6zGbYPe3KRVp',
     'contact': 'l.grzybek@pwsz.elblag.pl, p.kwasniewski@pwsz.elblag.pl',
     'enabled': True,
     },
    {'usos_id': 'EUHE',
     'name': 'Elbląska Uzelnia Humanistyczno-Ekonomiczna',
     'url': 'https://usosapps.euh-e.edu.pl/',
     'logo': '/static/img/logo/logo-euhe-64x64.jpg',
     'consumer_key': '5fWZYAdbSEkhvGXWTgmM',
     'consumer_secret': 'PhZjKtKvc553Epw7GZEtr2j6ZnEYkZuZFGSKLMvJ',
     'contact': 'admin@euh-e.edu.pl',
     'enabled': True,
     },
    {'usos_id': 'UMFC',  # z palca dodane
     'name': 'Uniwersytet Muzyczny Fryderyka Chopina w Warszawie',
     'url': 'https://usosapps.chopin.edu.pl/',
     'logo': '/static/img/logo/logo-umfc-64x64.jpg',
     'consumer_key': 'eJJcsMasd5wtUfGWp9pR',
     'consumer_secret': '4gjFFBGjSM4sndwwkUewAEz3XUGapTQ42NYDftbq',
     'contact': 'maksymilian.szpura@adm.uw.edu.pl',
     'enabled': True
     },
    {'usos_id': 'UPH',
     'name': 'Uniwersytet Przyrodniczo-Humanistyczny w Siedlcach',
     'url': 'https://usosapps.uph.edu.pl/',
     'logo': '/static/img/logo/logo-uph-64x64.jpg',
     'consumer_key': 'QmeQednVWmpYgSrAYWYc',
     'consumer_secret': '29YshXKxtAjPyz2UGkEa5XJ7DWDkqw5dESeWu92Y',
     'contact': 'usosweb@uph.edu.pl',
     'enabled': True
     },
     {'usos_id': 'DEMO',
      'name': 'Uniwersytet DEMO w Nibylandi',
      'url': 'https://usosapps.demo.usos.edu.pl/',
      'logo': '/static/img/logo/logo-demo-64x64.jpg',
      'consumer_key': 'u9xbMGsj9rfER3QBPCBR',
      'consumer_secret': 'f6TDvucnwDUJ8ZX7HCFa4kvNEFnE7MzByezgBy5v',
      'contact': 'dsksysadm@adm.uw.edu.pl',
      'enabled': True
    },
]
