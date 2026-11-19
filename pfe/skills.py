"""Skill name -> regex used to spot it in offer text. Profiles list skills by name; names missing here
fall back to a whole-word match, and a profile can override any pattern with `match:`."""
import re

CATALOG = {
    "java": r"\bjava\b(?!\s*script)",
    "spring boot": r"\bspring(\s*boot)?\b",
    "spring security": r"spring security|\bjwt\b|oauth|keycloak",
    "hibernate": r"hibernate|\bjpa\b",
    "angular": r"\bangular\b",
    "typescript": r"typescript",
    "react": r"\breact(\.?js)?\b(?!\s*native)",
    "react native": r"react\s*native",
    "vue": r"\bvue(\.?js)?\b",
    "next.js": r"next\.?js",
    "node.js": r"node\.?js|\bexpress(\.js)?\b|nestjs",
    "python": r"\bpython\b",
    "django": r"\bdjango\b",
    "fastapi": r"fastapi",
    "flask": r"\bflask\b",
    "javascript": r"javascript|\bjs\b",
    "kotlin": r"kotlin",
    "c": r"\blangage c\b|\bc\s*/\s*c\+\+|\bc,",
    "c++": r"c\+\+",
    "c#": r"c#|\.net\b",
    "php": r"\bphp\b",
    "laravel": r"laravel",
    "symfony": r"symfony",
    "sql": r"\bsql\b",
    "postgresql": r"postgre",
    "mysql": r"mysql",
    "mongodb": r"mongo",
    "oracle": r"\boracle\b",
    "redis": r"\bredis\b",
    "rest api": r"\brest(ful)?\b|\bapi(s)?\b",
    "graphql": r"graphql",
    "microservices": r"micro-?services?",
    "docker": r"docker|conteneur",
    "kubernetes": r"kubernetes|\bk8s\b",
    "git": r"\bgit\b|github|gitlab",
    "ci/cd": r"ci\s*/\s*cd|jenkins|github actions|gitlab ci",
    "linux": r"\blinux\b",
    "aws": r"\baws\b|amazon web services",
    "azure": r"\bazure\b",
    "gcp": r"\bgcp\b|google cloud",
    "full-stack": r"full[\s-]?stack|application web|plateforme web|web app",
    "llm": r"\bllms?\b|genai|ia g[ée]n[ée]rative|generative ai|gpt|chatbot|agents? (d'|d’)?ia|ai agent",
    "rag": r"\brag\b|retrieval|recherche s[ée]mantique|vector",
    "langchain": r"langchain|langgraph|llamaindex",
    "machine learning": r"machine learning|apprentissage automatique|scikit|\bml\b",
    "deep learning": r"deep learning|pytorch|tensorflow|keras|r[ée]seaux de neurones",
    "computer vision": r"\bvision\b|opencv|yolo",
    "ocr": r"\bocr\b|tesseract",
    "nlp": r"\bnlp\b|traitement (automatique )?du langage",
    "ai": r"\bia\b|\bai\b|intelligence artificielle",
    "pandas": r"pandas",
    "power bi": r"power\s*bi",
    "iot": r"\biot\b|objets connect|mqtt|esp32",
    "raspberry pi": r"raspberry",
    "arduino": r"arduino",
    "flutter": r"flutter|\bdart\b",
    "android": r"android",
    "figma": r"figma",
    "ui/ux": r"\bui\b|\bux\b|maquett",
    "testing": r"selenium|cypress|pytest|junit|tests? (unitaires|automatis)",
    "cybersecurity": r"cybers[ée]curit|pentest|\bsoc\b|siem",
    "networking": r"r[ée]seaux?|cisco|ccna",
    "sap": r"\bsap\b",
    "salesforce": r"salesforce",
    "legacy modernization": r"migration|moderni[sz]",
}


def pattern(name, override=None):
    rx = override or CATALOG.get(name.lower()) or rf"(?<!\w){re.escape(name.lower())}(?!\w)"
    return re.compile(rx, re.I)


def any_known(token):
    """True if a token from an offer's tech list matches some catalog skill (used for gap lists)."""
    return any(re.search(rx, token, re.I) for rx in CATALOG.values())
