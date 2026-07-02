from pubmed import save_topic
from topics import TOPICS


def main():
    print("=" * 60)
    print("Building Medical Knowledge Base")
    print("=" * 60)

    for topic in TOPICS:
        try:
            save_topic(topic)
        except Exception as e:
            print(f"Failed to download {topic}: {e}")

    print("\nKnowledge base build complete.")


if __name__ == "__main__":
    main()