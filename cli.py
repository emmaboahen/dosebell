import sys

from agent import run_conversation


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    prompt = " ".join(argv).strip()
    if not prompt:
        print('usage: dosebell "<what you want>"', file=sys.stderr)
        return 2

    messages = [{"role": "user", "content": prompt}]
    run_conversation(messages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
