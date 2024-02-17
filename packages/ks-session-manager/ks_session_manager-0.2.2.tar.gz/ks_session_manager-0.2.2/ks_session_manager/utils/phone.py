import re

COUNTRY_CODES = {
    "93": "afghanistan",
    "355": "albania",
    "684": "american_samoa",
    "376": "andorra",
    "244": "angola",
    "1264": "anguilla_anguilla",
    "1268": "antigua_and_barbuda",
    "374": "armenia",
    "54": "argentina",
    "61": "australia",
    "43": "austria",
    "994": "azerbaijan",
    "1242": "bahamas",
    "973": "bahrain",
    "880": "bangladesh",
    "1246": "barbados",
    "375": "belarus",
    "32": "belgium",
    "501": "belize",
    "229": "benin",
    "1441": "bermuda",
    "591": "bolivia",
    "387": "bosnia_and_herzegovina",
    "267": "botswana",
    "55": "brazil",
    "1284": "british_virgin_islands_british_virgin_islands",
    "673": "brunei_darusalaam",
    "359": "bulgaria",
    "226": "burkina_faso",
    "257": "burundi",
    "855": "cambodia",
    "237": "cameroon",
    "238": "cape_verde",
    "1345": "cayman_islands",
    "236": "central_african_republic",
    "235": "chad",
    "56": "chile",
    "86": "china",
    "57": "colombia",
    "1670": "commonwealth_of_the_northern_mariana_islands",
    "269": "comoros_and_mayotte_island",
    "242": "congo",
    "682": "cook_islands",
    "506": "costa_rica",
    "385": "croatia",
    "53": "cuba",
    "357": "cyprus",
    "420": "czech_republic",
    "45": "denmark",
    "246": "diego_garcia",
    "253": "djibouti",
    "1767": "dominica",
    "1809": "dominican_republic",
    "593": "ecuador",
    "20": "egypt",
    "503": "el_salvador",
    "240": "equatorial_guinea",
    "372": "estonia",
    "251": "ethiopia",
    "298": "faeroe_islands",
    "500": "falkland_islands",
    "679": "fiji",
    "358": "finland",
    "33": "france",
    "590": "french_antilles",
    "594": "french_guiana",
    "689": "french_polynesia",
    "241": "gabon",
    "220": "gambia",
    "995": "georgia",
    "49": "germany",
    "233": "ghana",
    "350": "gibraltar",
    "30": "greece",
    "299": "greenland",
    "1473": "grenada",
    "671": "guam",
    "502": "guatemala",
    "224": "guinea",
    "245": "guinea",
    "592": "guyana",
    "509": "haiti",
    "504": "honduras",
    "852": "hong_kong",
    "36": "hungary",
    "354": "iceland",
    "91": "india",
    "62": "indonesia",
    "98": "iran",
    "964": "iraq",
    "353": "irish_republic",
    "972": "israel",
    "39": "italy",
    "225": "ivory_coast",
    "1876": "jamaica",
    "81": "japan",
    "962": "jordan",
    "254": "kenya",
    "686": "kiribati_republic",
    "996": "kirg",
    "965": "kuwait",
    "856": "laos",
    "371": "latvia",
    "961": "lebanon",
    "266": "lesotho",
    "231": "liberia",
    "370": "lithuania",
    "352": "luxembourg",
    "853": "macao",
    "389": "macedonia",
    "261": "madagascar",
    "265": "malawi",
    "60": "malaysia",
    "960": "maldives",
    "223": "mali",
    "356": "malta",
    "692": "marshall_islands",
    "596": "martinique",
    "222": "mauritania",
    "230": "mauritius",
    "52": "mexico",
    "691": "micronesia",
    "377": "monaco",
    "976": "mongolia",
    "1664": "montserrat",
    "212": "morocco",
    "213": "algeria",
    "258": "mozambique",
    "95": "myanmar",
    "264": "namibia",
    "674": "nauru",
    "977": "nepal",
    "31": "netherlands",
    "599": "netherlands_antilles",
    "687": "new_caledonia",
    "64": "new_zealand",
    "505": "nicaragua",
    "227": "niger",
    "234": "nigeria",
    "683": "niue",
    "672": "norfolk_island",
    "850": "north_korea",
    "967": "north_yemen",
    "670": "northern_mariana_islands",
    "47": "norway",
    "968": "oman",
    "92": "pakistan",
    "507": "panama",
    "675": "papua_new_guinea",
    "595": "paraguay",
    "51": "peru",
    "63": "philippines",
    "48": "poland",
    "351": "portugal",
    "1787": "puerto_rico",
    "974": "qatar",
    "378": "republic_of_san_marino",
    "262": "reunion",
    "40": "romania",
    "7": "russia",
    "77": "kazakhstan",
    "250": "rwandese_republic",
    "247": "saint_helena_and_ascension_island",
    "508": "saint_pierre_et_miquelon",
    "239": "sao_tome_e_principe",
    "966": "saudi_arabia",
    "221": "senegal",
    "248": "seychelles",
    "232": "sierra_leone",
    "65": "singapore",
    "421": "slovakia",
    "386": "slovenia",
    "677": "solomon_islands",
    "252": "somalia",
    "27": "south_africa",
    "82": "south_korea",
    "969": "south_yemen",
    "34": "spain",
    "94": "sri_lanka",
    "1869": "st.kitts_and_nevis",
    "1758": "st.lucia",
    "1784": "st.vincent_and_the_grenadines",
    "249": "sudan",
    "597": "suriname",
    "268": "swaziland",
    "46": "sweden",
    "41": "switzerland",
    "963": "syria",
    "992": "tajikistan",
    "886": "taiwan",
    "255": "tanzania",
    "66": "thailand",
    "228": "togolese_republic",
    "690": "tokelau",
    "676": "tonga",
    "1868": "trinidad_and_tobago",
    "21": "tunisia",
    "90": "turkey",
    "993": "turkmenistan",
    "1649": "turks",
    "688": "tuvalu",
    "1340": "us_virgin_islands",
    "256": "uganda",
    "380": "ukraine",
    "971": "united_arab_emirates",
    "44": "united_kingdom",
    "598": "uruguay",
    "1": "usa",
    "998": "uzbekistan",
    "678": "vanuatu",
    "58": "venezuela",
    "84": "vietnam",
    "681": "wallis_and_futuna_islands",
    "685": "western_samoa",
    "381": "yugoslavia",
    "243": "zaire",
    "260": "zambia",
    "263": "zimbabwe",
}
NOT_PHONE_SYMBOLS = re.compile(r'\D')


def guess_country_by_phone_number(phone_number: str) -> str | None:
    """
    Guesses the country of a phone number based on the given phone number.

    Parameters:
        phone_number (str): The phone number to guess the country of.

    Returns:
        str: The guessed country of the phone number, or None if the phone number is empty or no country is found.

    """
    phone_number = clean_phone_number(phone_number)

    if not bool(phone_number):
        return None

    for country_code in sorted(COUNTRY_CODES.keys(), key=lambda item: -int(item)):
        if phone_number.startswith(country_code):
            return COUNTRY_CODES[country_code]

    return None


def is_valid_phone_number(phone_number: str) -> bool:
    """

    This method checks if a given phone number is valid.

    Parameters:
        phone_number (str): The phone number to be checked.

    Returns:
        bool: True if the phone number is valid, False otherwise.

    """
    return bool(re.match(r"^\d{7,15}$", phone_number))


def clean_phone_number(phone_number: str) -> str:
    """
    Cleans a phone number by removing all non-digit characters and validates if the resulting cleaned number is valid.

    Parameters:
        phone_number (str): The input phone number to clean.

    Returns:
        str: The cleaned phone number if it is valid, otherwise an empty string.

    """
    result = re.sub(r'\D', '', phone_number)

    if not is_valid_phone_number(result):
        return ""

    return result
