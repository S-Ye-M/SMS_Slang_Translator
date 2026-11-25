import argparse
from translator import SlangTranslator


def main():
    p = argparse.ArgumentParser(description="SMS Slang Translator (NLP)")
    p.add_argument("text", nargs="?", help="text to translate; omit for interactive mode")
    p.add_argument("--annotate", action="store_true", help="show 'BRB (Be Right Back)' style output")
    p.add_argument("--reverse", action="store_true", help="English -> slang")
    p.add_argument("--no-words", action="store_true", help="ignore slang words (fire, tea, slay...)")
    p.add_argument("--stats", action="store_true", help="print dictionary statistics")
    args = p.parse_args()
    t = SlangTranslator()
    if args.stats:
        s = t.stats()
        print(f"Total entries: {s['total']}")
        for c, n in sorted(s["by_category"].items(), key=lambda x: -x[1]):
            print(f"  {c:<24}{n}")
        return
    run = (t.to_slang if args.reverse
           else lambda s: t.translate(s, args.annotate, include_words=not args.no_words))
    if args.text:
        print(run(args.text))
        return
    print("Interactive mode (Ctrl+C to exit)")
    while True:
        try:
            print("->", run(input("> ")))
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    main()
