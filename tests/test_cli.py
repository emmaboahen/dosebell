import cli


def test_main_joins_arguments_into_prompt(monkeypatch):
    captured = {}

    def fake_run_conversation(messages):
        captured["messages"] = messages
        return messages

    monkeypatch.setattr(cli, "run_conversation", fake_run_conversation)

    code = cli.main(["remind", "me", "to", "take", "meds", "at", "8am"])

    assert code == 0
    assert captured["messages"] == [
        {"role": "user", "content": "remind me to take meds at 8am"}
    ]


def test_main_without_prompt_prints_usage(capsys):
    code = cli.main([])

    assert code == 2
    assert "usage: dosebell" in capsys.readouterr().err
