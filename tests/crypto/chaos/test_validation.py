from lattence_crypto.chaos import (
    CryptoChaosObservation,
    validate_downgrade_resistance,
)


def _observation(
    experiment: str,
    *,
    accepted: bool | None,
    executed: bool = True,
    timed_out: bool = False,
) -> CryptoChaosObservation:
    return CryptoChaosObservation(
        experiment=experiment,
        target_path="tls.conf",
        executed=executed,
        downgrade_accepted=accepted,
        timed_out=timed_out,
        probe_returncode=0 if accepted else 1,
        rollback_verified=True,
        original_sha256="a" * 64,
        mutated_sha256="b" * 64 if executed else None,
    )


def test_downgrade_validation_requires_every_probe_to_reject() -> None:
    result = validate_downgrade_resistance(
        (
            _observation("signature-downgrade", accepted=False),
            _observation("key-exchange-downgrade", accepted=False),
        )
    )

    assert result.status == "resistant"
    assert result.resistant is True
    assert [item.experiment for item in result.evidence] == [
        "key-exchange-downgrade",
        "signature-downgrade",
    ]
    assert all(item.outcome == "rejected" for item in result.evidence)


def test_downgrade_validation_reports_accepted_downgrade() -> None:
    result = validate_downgrade_resistance(
        (_observation("key-exchange-downgrade", accepted=True),)
    )

    assert result.status == "vulnerable"
    assert result.resistant is False
    assert result.evidence[0].outcome == "accepted"


def test_downgrade_validation_blocks_on_incomplete_observation() -> None:
    result = validate_downgrade_resistance(
        (
            _observation(
                "key-exchange-downgrade",
                accepted=None,
                timed_out=True,
            ),
        )
    )

    assert result.status == "blocked"
    assert result.resistant is None
    assert result.evidence[0].outcome == "timeout"
    assert "one or more probes timed out" in result.blocking_reasons
