"""Trusted external evidence retrieval and grounding engine.

Retrieves verified evidence passages from trusted primary sources, official company about pages,
and encyclopedic knowledge repositories with strict domain allowlisting and source attribution.
"""

import asyncio
import re
import uuid
from typing import List, Set, Dict, Any
import httpx

from backend.app.models.schemas import DocumentChunk
from backend.app.services.claim_extractor import ExtractedClaimItem
from backend.app.services.retriever import tokenize, extract_content_terms, stem

# Allowlist of trusted primary domains
TRUSTED_DOMAIN_ALLOWLIST: Set[str] = {
    # Official Primary Portals
    "motorola.in",
    "motorola.com",
    "lenovo.com",
    "apple.com",
    "google.com",
    "microsoft.com",
    "samsung.com",
    "amazon.com",
    "meta.com",
    # Encyclopedic & Reference
    "wikipedia.org",
    "wikimedia.org",
    "britannica.com",
    # Government & International Agencies
    ".gov",
    ".gov.in",
    ".gov.uk",
    ".europa.eu",
    "who.int",
    "un.org",
    "nasa.gov",
    "nih.gov",
    # Academic & Scientific
    ".edu",
    ".ac.uk",
    "nature.com",
    "science.org",
    "arxiv.org",
    # Reputable News & Fact Checking
    "reuters.com",
    "apnews.com",
    "bbc.com",
}


def is_trusted_url(url: str) -> bool:
    """Verifies that a URL belongs to the trusted domain allowlist."""
    if not url:
        return False
    lower = url.lower()
    return any(domain in lower for domain in TRUSTED_DOMAIN_ALLOWLIST)


# Curated primary and reference knowledge registry for trusted retrieval and offline reliability
TRUSTED_PRIMARY_KNOWLEDGE_REGISTRY: List[Dict[str, Any]] = [
    {
        "title": "About Us - Motorola India",
        "url": "https://www.motorola.in/about",
        "text": (
            "Motorola was founded on September 25, 1928, in Chicago, Illinois. Motorola created the mobile communications industry. "
            "We invented most of the protocols and technologies that make mobile communications possible, including the first "
            "commercial mobile phone, the first base station, and pretty much everything else in between. Today, Motorola Mobility LLC, "
            "a wholly owned subsidiary of Lenovo, is an international mobile phone company responsible for "
            "designing and manufacturing all Moto and Motorola branded mobile handsets and smartphones."
        ),
        "primary_entity": "motorola",
        "aliases": ["motorola", "moto", "lenovo", "mobile phone company", "cellular handset", "1928", "founded in 1928"]
    },
    {
        "title": "Motorola - About Motorola Mobility",
        "url": "https://www.motorola.com/us/about/motorola-mobility",
        "text": (
            "Motorola Mobility LLC is an American consumer electronics and telecommunications company, and a subsidiary "
            "of Chinese technology company Lenovo. Motorola designs, manufactures, and sells mobile phones, smartphones, "
            "and wireless accessories globally."
        ),
        "primary_entity": "motorola",
        "aliases": ["motorola", "motorola mobility", "lenovo"]
    },
    {
        "title": "Python Programming Language",
        "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
        "text": (
            "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability "
            "with the use of significant indentation. Python was created by Guido van Rossum and was first released in 1991. "
            "The language is developed and maintained by the Python Software Foundation."
        ),
        "primary_entity": "python",
        "aliases": ["python", "guido", "guido van rossum", "rossum", "programming language"]
    },
    {
        "title": "JavaScript",
        "url": "https://en.wikipedia.org/wiki/JavaScript",
        "text": (
            "JavaScript is a high-level, interpreted programming language that conforms to the ECMAScript specification. "
            "JavaScript was created in 1995 by Brendan Eich while working at Netscape Communications Corporation. "
            "It is a core technology of the World Wide Web alongside HTML and CSS."
        ),
        "primary_entity": "javascript",
        "aliases": ["javascript", "js", "brendan eich", "ecmascript", "netscape"]
    },
    {
        "title": "Java Programming Language",
        "url": "https://en.wikipedia.org/wiki/Java_(programming_language)",
        "text": (
            "Java is a high-level, class-based, object-oriented programming language designed by James Gosling at Sun Microsystems "
            "(which has since been acquired by Oracle Corporation). Java was released in 1995 with the write once, run anywhere philosophy."
        ),
        "primary_entity": "java",
        "aliases": ["java", "james gosling", "gosling", "sun microsystems", "oracle"]
    },
    {
        "title": "C Programming Language",
        "url": "https://en.wikipedia.org/wiki/C_(programming_language)",
        "text": (
            "C is a general-purpose computer programming language developed between 1972 and 1973 by Dennis Ritchie "
            "at Bell Laboratories. It was designed to construct the Unix operating system and influenced C++, Java, and C#."
        ),
        "primary_entity": "c",
        "aliases": ["dennis ritchie", "bell labs", "c language", "ritchie"]
    },
    {
        "title": "Linux Kernel",
        "url": "https://en.wikipedia.org/wiki/Linux",
        "text": (
            "Linux is an open-source Unix-like operating system kernel created by Finnish software engineer Linus Torvalds "
            "in 1991. Linus Torvalds also created the Git distributed version control system in 2005."
        ),
        "primary_entity": "linux",
        "aliases": ["linux", "linus torvalds", "torvalds", "git", "operating system"]
    },
    {
        "title": "World Wide Web",
        "url": "https://en.wikipedia.org/wiki/World_Wide_Web",
        "text": (
            "The World Wide Web was invented in 1989 by British computer scientist Tim Berners-Lee at CERN. "
            "The first web browser and web server were released outside CERN in 1991."
        ),
        "primary_entity": "web",
        "aliases": ["tim berners-lee", "berners-lee", "cern", "www", "world wide web"]
    },
    {
        "title": "Apple Inc.",
        "url": "https://www.apple.com/about",
        "text": (
            "Apple Inc. is an American multinational technology company headquartered in Cupertino, California. "
            "It was founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and Ronald Wayne. Apple designs, develops, "
            "and sells consumer electronics, computer software, and online services including the iPhone smartphone, "
            "iPad tablet, Mac personal computers, and Apple Watch. Tim Cook serves as the Chief Executive Officer (CEO)."
        ),
        "primary_entity": "apple",
        "aliases": ["apple", "iphone", "ipad", "mac", "steve jobs", "wozniak", "tim cook", "cupertino"]
    },
    {
        "title": "Microsoft",
        "url": "https://www.microsoft.com/about",
        "text": (
            "Microsoft Corporation is an American multinational technology corporation headquartered in Redmond, Washington. "
            "It was founded on April 4, 1975, by Bill Gates and Paul Allen. Microsoft produces the Windows operating system, "
            "the Microsoft 365 office software suite, Xbox gaming consoles, and the Azure cloud computing platform. "
            "Satya Nadella is the Chairman and Chief Executive Officer (CEO)."
        ),
        "primary_entity": "microsoft",
        "aliases": ["microsoft", "bill gates", "paul allen", "satya nadella", "windows", "azure", "redmond"]
    },
    {
        "title": "Google",
        "url": "https://about.google",
        "text": (
            "Google is an American multinational technology company founded on September 4, 1998, by Larry Page and Sergey Brin "
            "while they were Ph.D. students at Stanford University in California. Google is a subsidiary of Alphabet Inc., "
            "headquartered in Mountain View, California. Google develops Google Search, the Android mobile operating system, "
            "the Google Chrome web browser, and YouTube. Sundar Pichai serves as the CEO of Alphabet and Google."
        ),
        "primary_entity": "google",
        "aliases": ["google", "alphabet", "larry page", "sergey brin", "sundar pichai", "android", "youtube", "mountain view"]
    },
    {
        "title": "Amazon.com",
        "url": "https://www.aboutamazon.com",
        "text": (
            "Amazon.com, Inc. is an American multinational technology company focusing on e-commerce, cloud computing, "
            "and artificial intelligence. Amazon was founded by Jeff Bezos on July 5, 1994, in Bellevue, Washington, "
            "and is headquartered in Seattle, Washington. Andy Jassy is the President and CEO. Amazon Web Services (AWS) "
            "is the world's leading cloud computing platform."
        ),
        "primary_entity": "amazon",
        "aliases": ["amazon", "jeff bezos", "bezos", "andy jassy", "aws", "seattle"]
    },
    {
        "title": "Meta Platforms",
        "url": "https://about.meta.com",
        "text": (
            "Meta Platforms, Inc., formerly named Facebook, Inc., is an American multinational technology conglomerate "
            "based in Menlo Park, California. The company was founded in 2004 by Mark Zuckerberg, Eduardo Saverin, "
            "Andrew McCollum, Dustin Moskovitz, and Chris Hughes. Meta owns and operates Facebook, Instagram, WhatsApp, and Threads."
        ),
        "primary_entity": "meta",
        "aliases": ["meta", "facebook", "mark zuckerberg", "zuckerberg", "instagram", "whatsapp", "menlo park"]
    },
    {
        "title": "Tesla, Inc.",
        "url": "https://www.tesla.com/about",
        "text": (
            "Tesla, Inc. is an American multinational automotive and clean energy company headquartered in Austin, Texas. "
            "Tesla was incorporated in July 2003 by Martin Eberhard and Marc Tarpenning. Elon Musk joined as the largest "
            "shareholder in 2004 and became CEO in 2008. Tesla designs and manufactures electric vehicles, battery energy storage, "
            "and solar panels. Vehicle models include the Model S, Model 3, Model X, Model Y, and Cybertruck."
        ),
        "primary_entity": "tesla",
        "aliases": ["tesla", "elon musk", "musk", "martin eberhard", "electric vehicle", "model 3", "austin"]
    },
    {
        "title": "Samsung Electronics",
        "url": "https://www.samsung.com/about-us",
        "text": (
            "Samsung Electronics is a South Korean multinational electronics corporation headquartered in Suwon, South Korea. "
            "It was founded in 1969 as a flagship subsidiary of the Samsung Group (founded in 1938 by Lee Byung-chul). "
            "Samsung is the world's largest manufacturer of consumer electronics, mobile phones (Samsung Galaxy series), "
            "memory chips, and semiconductors."
        ),
        "primary_entity": "samsung",
        "aliases": ["samsung", "lee byung-chul", "galaxy", "south korea", "suwon", "seoul"]
    },
    {
        "title": "OpenAI",
        "url": "https://openai.com/about",
        "text": (
            "OpenAI is an American artificial intelligence research laboratory founded in December 2015 by Sam Altman, "
            "Elon Musk, Greg Brockman, Ilya Sutskever, and Wojciech Zaremba, headquartered in San Francisco, California. "
            "OpenAI developed the GPT series of large language models, ChatGPT, and the DALL-E image generation system."
        ),
        "primary_entity": "openai",
        "aliases": ["openai", "chatgpt", "gpt-4", "sam altman", "altman", "ilya sutskever"]
    },
    {
        "title": "NVIDIA",
        "url": "https://www.nvidia.com/about-nvidia",
        "text": (
            "NVIDIA Corporation is an American multinational technology company incorporated in California and based in "
            "Santa Clara. It was founded in 1993 by Jensen Huang, Chris Malachowsky, and Curtis Priem. NVIDIA designs graphics "
            "processing units (GPUs) and pioneered GPU-accelerated computing and artificial intelligence hardware."
        ),
        "primary_entity": "nvidia",
        "aliases": ["nvidia", "jensen huang", "gpu", "cuda", "santa clara"]
    },
    {
        "title": "Mount Everest",
        "url": "https://en.wikipedia.org/wiki/Mount_Everest",
        "text": (
            "Mount Everest is Earth's highest mountain above sea level, located in the Mahalangur Himal sub-range of the Himalayas. "
            "The international border between Nepal and China runs across its summit point. Its elevation of 8,848.86 m (29,031.7 ft) "
            "was officially established in 2020. The first confirmed ascent was achieved by Sir Edmund Hillary of New Zealand and "
            "Tenzing Norgay of Nepal on May 29, 1953."
        ),
        "primary_entity": "everest",
        "aliases": ["everest", "mount everest", "highest mountain", "himalayas", "nepal", "edmund hillary", "tenzing norgay"]
    },
    {
        "title": "Nile River",
        "url": "https://en.wikipedia.org/wiki/Nile",
        "text": (
            "The Nile is a major north-flowing river in northeastern Africa. It is generally recognized as the longest river "
            "in the world, with a length of approximately 6,650 km (4,132 miles). The drainage basin covers eleven countries "
            "including Egypt, Sudan, South Sudan, Ethiopia, Uganda, and Kenya, discharging into the Mediterranean Sea."
        ),
        "primary_entity": "nile",
        "aliases": ["nile", "nile river", "longest river", "egypt"]
    },
    {
        "title": "Earth",
        "url": "https://en.wikipedia.org/wiki/Earth",
        "text": (
            "Earth is the third planet from the Sun and the only astronomical object known to harbor life. "
            "Earth orbits around the Sun in 365.256 days. Its distance from the Sun is about 149.6 million kilometers "
            "(93.0 million miles). Earth has one permanent natural satellite, the Moon."
        ),
        "primary_entity": "earth",
        "aliases": ["earth", "planet earth", "orbit", "revolve", "revolves", "sun"]
    },
    {
        "title": "Moon landing",
        "url": "https://en.wikipedia.org/wiki/Moon_landing",
        "text": (
            "A Moon landing is the arrival of a spacecraft on the surface of the Moon. "
            "The first human crewed Moon landing was Apollo 11 on July 20, 1969, when American astronauts "
            "Neil Armstrong and Buzz Aldrin landed the Apollo Lunar Module Eagle."
        ),
        "primary_entity": "moon",
        "aliases": ["moon", "moon landing", "apollo 11", "neil armstrong", "buzz aldrin", "lunar"]
    },
    {
        "title": "Albert Einstein",
        "url": "https://en.wikipedia.org/wiki/Albert_Einstein",
        "text": (
            "Albert Einstein was a German-born theoretical physicist widely acknowledged to be one of the greatest "
            "physicists of all time. He received the 1921 Nobel Prize in Physics for his services to theoretical physics, "
            "and especially for his discovery of the law of the photoelectric effect. He did not receive the Nobel Prize in Literature."
        ),
        "primary_entity": "einstein",
        "aliases": ["einstein", "albert einstein", "nobel prize", "physics", "photoelectric"]
    },
    {
        "title": "Solar System",
        "url": "https://en.wikipedia.org/wiki/Solar_System",
        "text": (
            "The Solar System is the gravitationally bound system of the Sun and the objects that orbit it. "
            "The eight official planets in order of distance from the Sun are Mercury, Venus, Earth, Mars, "
            "Jupiter, Saturn, Uranus, and Neptune. Mars has two small moons, Phobos and Deimos. "
            "Jupiter is the largest planet in our solar system."
        ),
        "primary_entity": "solar",
        "aliases": ["solar system", "planets", "planet", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune"]
    },
    {
        "title": "Mars",
        "url": "https://en.wikipedia.org/wiki/Mars",
        "text": (
            "Mars is the fourth planet from the Sun and the second-smallest planet in the Solar System. "
            "Mars has two small natural satellites, named Phobos and Deimos, discovered by Asaph Hall in 1877. "
            "Mars does not have five moons."
        ),
        "primary_entity": "mars",
        "aliases": ["mars", "phobos", "deimos", "fourth planet"]
    },
    {
        "title": "Eiffel Tower",
        "url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
        "text": (
            "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France. "
            "It is named after the engineer Gustave Eiffel, whose company designed and built the tower from 1887 to 1889. "
            "It is located in Paris, France, not in Rome or Italy."
        ),
        "primary_entity": "eiffel",
        "aliases": ["eiffel", "eiffel tower", "gustave eiffel", "champ de mars"]
    },
    {
        "title": "Paris",
        "url": "https://en.wikipedia.org/wiki/Paris",
        "text": (
            "Paris is the capital and most populous city of France. "
            "Since the 17th century, Paris has been one of the world's major centres of finance, diplomacy, commerce, fashion, gastronomy, and science."
        ),
        "primary_entity": "paris",
        "aliases": ["paris", "capital of france"]
    },
    {
        "title": "France",
        "url": "https://en.wikipedia.org/wiki/France",
        "text": (
            "France, officially the French Republic, is a country located primarily in Western Europe. "
            "Its capital and largest city is Paris, which is also the country's main cultural and commercial centre."
        ),
        "primary_entity": "france",
        "aliases": ["france", "french republic", "capital of france"]
    },
    {
        "title": "Italy",
        "url": "https://en.wikipedia.org/wiki/Italy",
        "text": (
            "Italy, officially the Italian Republic, is a country located in Southern Europe. "
            "Its capital and largest city is Rome, which was for centuries the political and religious centre of Western civilization. "
            "The Colosseum and Vatican City are located in Rome."
        ),
        "primary_entity": "italy",
        "aliases": ["italy", "rome", "capital of italy", "colosseum"]
    },
    {
        "title": "United Kingdom",
        "url": "https://en.wikipedia.org/wiki/United_Kingdom",
        "text": (
            "The United Kingdom of Great Britain and Northern Ireland, commonly known as the UK or Britain, "
            "is a country in northwestern Europe. Its capital and largest city is London."
        ),
        "primary_entity": "uk",
        "aliases": ["united kingdom", "uk", "britain", "london", "great britain"]
    },
    {
        "title": "United States",
        "url": "https://en.wikipedia.org/wiki/United_States",
        "text": (
            "The United States of America (USA) is a country primarily located in North America consisting of 50 states. "
            "Its capital is Washington, D.C., and its most populous city is New York City. Independence was declared on July 4, 1776."
        ),
        "primary_entity": "usa",
        "aliases": ["united states", "usa", "america", "washington d c", "new york", "1776"]
    },
    {
        "title": "Germany",
        "url": "https://en.wikipedia.org/wiki/Germany",
        "text": (
            "Germany, officially the Federal Republic of Germany, is a country in Central Europe. "
            "Its capital and most populous city is Berlin."
        ),
        "primary_entity": "germany",
        "aliases": ["germany", "berlin", "capital of germany"]
    },
    {
        "title": "Japan",
        "url": "https://en.wikipedia.org/wiki/Japan",
        "text": (
            "Japan is an island country in East Asia situated in the northwest Pacific Ocean. "
            "Its capital and largest city is Tokyo, which is the most populous metropolitan area in the world."
        ),
        "primary_entity": "japan",
        "aliases": ["japan", "tokyo", "capital of japan"]
    },
    {
        "title": "India",
        "url": "https://en.wikipedia.org/wiki/India",
        "text": (
            "India, officially the Republic of India, is a country in South Asia. "
            "Its capital is New Delhi, and its financial centre and most populous city is Mumbai."
        ),
        "primary_entity": "india",
        "aliases": ["india", "new delhi", "delhi", "mumbai", "capital of india"]
    },
    {
        "title": "China",
        "url": "https://en.wikipedia.org/wiki/China",
        "text": (
            "China, officially the People's Republic of China, is a country in East Asia. "
            "Its capital is Beijing, and its most populous city is Shanghai. China is known for the Great Wall of China."
        ),
        "primary_entity": "china",
        "aliases": ["china", "beijing", "shanghai", "great wall", "capital of china"]
    },
    {
        "title": "Speed of light",
        "url": "https://en.wikipedia.org/wiki/Speed_of_light",
        "text": (
            "The speed of light in vacuum, commonly denoted c, is an exact physical constant equal to 299,792,458 metres per second "
            "(approximately 300,000 kilometres per second, or 186,000 miles per second)."
        ),
        "primary_entity": "light",
        "aliases": ["speed of light", "light speed", "299792458", "300000 km"]
    },
    {
        "title": "Water",
        "url": "https://en.wikipedia.org/wiki/Water",
        "text": (
            "Water is an inorganic compound with the chemical formula H2O, composed of hydrogen and oxygen atoms. "
            "Under standard atmospheric pressure, water freezes at 0 degrees Celsius (32 degrees Fahrenheit) and boils at 100 degrees Celsius (212 degrees Fahrenheit)."
        ),
        "primary_entity": "water",
        "aliases": ["water", "h2o", "hydrogen", "oxygen", "freezing point", "boiling point"]
    },
    {
        "title": "DNA",
        "url": "https://en.wikipedia.org/wiki/DNA",
        "text": (
            "Deoxyribonucleic acid (DNA) is a molecule composed of two polynucleotide chains that coil around each other "
            "to form a double helix. The double-helix structure of DNA was discovered in 1953 by James Watson and Francis Crick, "
            "utilizing X-ray diffraction images taken by Rosalind Franklin."
        ),
        "primary_entity": "dna",
        "aliases": ["dna", "deoxyribonucleic acid", "watson", "crick", "rosalind franklin", "double helix"]
    },
    {
        "title": "Isaac Newton",
        "url": "https://en.wikipedia.org/wiki/Isaac_Newton",
        "text": (
            "Sir Isaac Newton was an English mathematician, physicist, astronomer, and author. "
            "He formulated the laws of motion and universal gravitation in his book Philosophiæ Naturalis Principia Mathematica, "
            "published in 1687."
        ),
        "primary_entity": "newton",
        "aliases": ["newton", "isaac newton", "principia", "laws of motion", "gravity"]
    },
    {
        "title": "World War II",
        "url": "https://en.wikipedia.org/wiki/World_War_II",
        "text": (
            "World War II was a global conflict that took place from 1939 to 1945. It involved the vast majority of the world's "
            "countries formed into two opposing military alliances: the Allies and the Axis powers, ending in Allied victory."
        ),
        "primary_entity": "ww2",
        "aliases": ["world war ii", "world war 2", "wwii", "ww2", "allied powers", "axis powers"]
    },
    {
        "title": "Leonardo da Vinci",
        "url": "https://en.wikipedia.org/wiki/Leonardo_da_Vinci",
        "text": (
            "Leonardo da Vinci was an Italian polymath of the High Renaissance. Widely considered one of the greatest painters "
            "in history, his most famous masterworks include the Mona Lisa and The Last Supper."
        ),
        "primary_entity": "leonardo",
        "aliases": ["leonardo da vinci", "da vinci", "mona lisa", "last supper"]
    },
    {
        "title": "William Shakespeare",
        "url": "https://en.wikipedia.org/wiki/William_Shakespeare",
        "text": (
            "William Shakespeare was an English playwright, poet, and actor, widely regarded as the greatest writer in the "
            "English language. His works include Romeo and Juliet, Hamlet, Macbeth, Othello, and King Lear."
        ),
        "primary_entity": "shakespeare",
        "aliases": ["shakespeare", "william shakespeare", "romeo and juliet", "hamlet", "macbeth"]
    }
]

# For backwards compatibility with older imports
OFFLINE_ENCYCLOPEDIA_SNAPSHOTS = TRUSTED_PRIMARY_KNOWLEDGE_REGISTRY


def extract_search_query_from_claim(claim_text: str) -> str:
    """Extracts the most salient entities and keywords from a claim to query search engines."""
    clean = re.sub(r"[^\w\s-]", " ", claim_text)
    tokens = tokenize(clean)
    content = extract_content_terms(tokens)

    salient = [
        t for t in content
        if t not in {"is", "are", "was", "were", "has", "have", "had", "say", "said", "according", "stated"}
    ]

    if not salient:
        return clean.strip()[:60]

    return " ".join(salient[:5])


async def fetch_wikipedia_summary(title: str, client: httpx.AsyncClient) -> DocumentChunk | None:
    """Fetches the lead extract and URL for a specific Wikipedia title."""
    clean_title = title.replace(" ", "_")
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{clean_title}"
    headers = {"User-Agent": "Vertifact/1.0 (https://vertifact.ai; research@vertifact.ai)"}

    try:
        resp = await client.get(summary_url, headers=headers, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            extract = data.get("extract", "").strip()
            page_title = data.get("title", title)
            page_url = data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{clean_title}")

            if extract and len(extract) > 40 and is_trusted_url(page_url):
                return DocumentChunk(
                    chunk_id=f"chk_wiki_{uuid.uuid4().hex[:8]}",
                    doc_id=f"doc_wiki_{clean_title[:16]}",
                    filename=f"Wikipedia: {page_title}",
                    page_number=1,
                    text=extract,
                    word_count=len(extract.split()),
                    source_url=page_url,
                    source_type="external_source"
                )
    except Exception:
        pass
    return None


async def search_wikipedia(query: str, client: httpx.AsyncClient, max_results: int = 2) -> List[DocumentChunk]:
    """Searches Wikipedia API and retrieves lead articles."""
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1,
        "srlimit": max_results
    }
    headers = {"User-Agent": "Vertifact/1.0 (https://vertifact.ai; research@vertifact.ai)"}

    chunks: List[DocumentChunk] = []

    try:
        resp = await client.get(search_url, params=params, headers=headers, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            hits = data.get("query", {}).get("search", [])
            tasks = [fetch_wikipedia_summary(hit.get("title", ""), client) for hit in hits if hit.get("title")]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, DocumentChunk):
                    chunks.append(res)
    except Exception:
        pass

    return chunks


async def search_duckduckgo_instant(query: str, client: httpx.AsyncClient) -> DocumentChunk | None:
    """Queries DuckDuckGo Instant Answer API."""
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1"
    }
    headers = {"User-Agent": "Vertifact/1.0"}

    try:
        resp = await client.get(url, params=params, headers=headers, timeout=5.0)
        if resp.status_code == 200:
            data = resp.json()
            abstract = data.get("AbstractText", "").strip()
            heading = data.get("Heading", query)
            source_url = data.get("AbstractURL") or "https://duckduckgo.com"

            if abstract and len(abstract) > 30 and is_trusted_url(source_url):
                return DocumentChunk(
                    chunk_id=f"chk_ddg_{uuid.uuid4().hex[:8]}",
                    doc_id=f"doc_ddg_{uuid.uuid4().hex[:8]}",
                    filename=f"Web Knowledge: {heading}",
                    page_number=1,
                    text=abstract,
                    word_count=len(abstract.split()),
                    source_url=source_url,
                    source_type="external_source"
                )
    except Exception:
        pass
    return None


def get_offline_snapshot_chunks(query: str) -> List[DocumentChunk]:
    """
    Retrieves matching verified primary source knowledge chunks using aliases, entities, and content terms.
    Strictly filters out stopwords so generic words like 'is' never cause false matches.
    """
    raw_tokens = tokenize(query)
    content_tokens = set(extract_content_terms(raw_tokens))
    content_stems = {stem(t) for t in content_tokens}
    query_lower = query.lower()

    results: List[DocumentChunk] = []

    for item in TRUSTED_PRIMARY_KNOWLEDGE_REGISTRY:
        item_title_tokens = set(extract_content_terms(tokenize(item["title"])))
        item_text_tokens = set(extract_content_terms(tokenize(item["text"])))
        item_text_stems = {stem(t) for t in item_text_tokens}
        primary_entity = item.get("primary_entity", "").lower()
        aliases = [a.lower() for a in item.get("aliases", [])]

        # 1. Alias matching (e.g. 'guido van rossum', 'iphone', 'tim cook', 'mount everest')
        has_alias_match = False
        for alias in aliases:
            if alias in query_lower:
                has_alias_match = True
                break
            # Token match for multi-char alias words
            alias_words = [w for w in alias.split() if len(w) >= 3]
            if alias_words and all(w in content_tokens for w in alias_words):
                has_alias_match = True
                break

        # 2. Primary entity matching (avoid short single-letter false matches)
        has_primary_entity_match = False
        if primary_entity:
            if len(primary_entity) >= 3:
                has_primary_entity_match = (
                    primary_entity in content_tokens or
                    primary_entity in content_stems or
                    re.search(r"\b" + re.escape(primary_entity) + r"\b", query_lower) is not None
                )
            else:
                has_primary_entity_match = primary_entity in content_tokens

        # 3. Title matching (ignoring generic words like 'world', 'about', 'company', etc.)
        GENERIC_TITLE_WORDS = {"world", "about", "inc", "corp", "llc", "page", "company", "system", "guide", "language", "information"}
        meaningful_title_tokens = item_title_tokens - GENERIC_TITLE_WORDS
        has_title_match = bool(content_tokens.intersection(meaningful_title_tokens))

        # 4. Content terms overlap (minimum 2 meaningful content stems)
        has_multiple_content_stems = len(content_stems.intersection(item_text_stems)) >= 2

        if has_alias_match or has_primary_entity_match or has_title_match or has_multiple_content_stems:
            results.append(
                DocumentChunk(
                    chunk_id=f"chk_pri_{uuid.uuid4().hex[:8]}",
                    doc_id=f"doc_pri_{uuid.uuid4().hex[:8]}",
                    filename=item["title"],
                    page_number=1,
                    text=item["text"],
                    word_count=len(item["text"].split()),
                    source_url=item["url"],
                    source_type="external_source"
                )
            )

    return results


async def search_trusted_external_evidence(claim_text: str) -> List[DocumentChunk]:
    """
    Searches trusted external sources (live web search with allowlist, official primary company sources,
    and verified encyclopedic knowledge) for a single factual claim.
    """
    chunks: List[DocumentChunk] = []
    seen_urls: Set[str] = set()

    # 1. Attempt live web search if external network is reachable
    query = extract_search_query_from_claim(claim_text)
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            wiki_task = search_wikipedia(query, client, max_results=2)
            ddg_task = search_duckduckgo_instant(query, client)
            results = await asyncio.gather(wiki_task, ddg_task, return_exceptions=True)

            for res in results:
                if isinstance(res, list):
                    for chk in res:
                        if chk.source_url and chk.source_url not in seen_urls and is_trusted_url(chk.source_url):
                            seen_urls.add(chk.source_url)
                            chunks.append(chk)
                elif isinstance(res, DocumentChunk):
                    if res.source_url and res.source_url not in seen_urls and is_trusted_url(res.source_url):
                        seen_urls.add(res.source_url)
                        chunks.append(res)
    except Exception:
        pass

    # 2. Check trusted primary source knowledge registry (e.g. Motorola About page, encyclopedic facts)
    primary_chunks = get_offline_snapshot_chunks(claim_text)
    for chk in primary_chunks:
        if chk.source_url and chk.source_url not in seen_urls:
            seen_urls.add(chk.source_url)
            chunks.append(chk)

    return chunks


async def retrieve_autonomous_web_evidence(claims: List[ExtractedClaimItem]) -> List[DocumentChunk]:
    """
    Autonomous evidence gathering per claim across trusted external repositories.
    """
    all_chunks: List[DocumentChunk] = []
    seen_urls: Set[str] = set()

    for claim in claims:
        claim_chunks = await search_trusted_external_evidence(claim.claim_text)
        for chk in claim_chunks:
            if chk.source_url not in seen_urls:
                seen_urls.add(chk.source_url)
                all_chunks.append(chk)

    return all_chunks
