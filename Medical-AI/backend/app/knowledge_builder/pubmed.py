import os
import requests
import xml.etree.ElementTree as ET

# -----------------------------
# API URLs
# -----------------------------

SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# Folder where knowledge will be saved
KNOWLEDGE_DIR = "app/knowledge"

os.makedirs(KNOWLEDGE_DIR, exist_ok=True)


# -----------------------------
# Search PubMed
# -----------------------------

def search_pubmed(query, max_results=5):

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": max_results
    }

    response = requests.get(
        SEARCH_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["esearchresult"]["idlist"]


# -----------------------------
# Download Abstract
# -----------------------------

def fetch_article(pubmed_id):

    params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "xml"
    }

    response = requests.get(
        FETCH_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    root = ET.fromstring(response.text)

    title = ""

    abstract = ""

    title_node = root.find(".//ArticleTitle")

    if title_node is not None:

        title = "".join(title_node.itertext())


    abstract_nodes = root.findall(".//AbstractText")

    for node in abstract_nodes:

        abstract += "".join(node.itertext())

        abstract += "\n\n"


    return title, abstract


# -----------------------------
# Save Knowledge
# -----------------------------

def save_topic(topic):

    print(f"\nDownloading {topic}...")

    ids = search_pubmed(topic)

    if not ids:

        print("No articles found.")

        return


    filename = topic.lower().replace(" ", "_") + ".txt"

    filepath = os.path.join(KNOWLEDGE_DIR, filename)


    with open(filepath, "w", encoding="utf-8") as f:

        for pubmed_id in ids:

            title, abstract = fetch_article(pubmed_id)

            f.write("=" * 80 + "\n")

            f.write(title + "\n\n")

            f.write(abstract)

            f.write("\n\n")


    print(f"Saved to {filepath}")


# -----------------------------
# Test
# -----------------------------

if __name__ == "__main__":

    save_topic("Hypertension")