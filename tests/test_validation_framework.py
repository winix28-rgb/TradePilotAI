from tradepilotai_os.validation import run_validation_suite
from tradepilotai_os.validation import runner as validation_runner


def test_validation_suite_passes_all_modules():
    result = run_validation_suite()

    assert result.overall_status == "PASS"
    assert result.overall_score == 100.0
    assert result.total_modules == 6
    assert all(module.status == "PASS" for module in result.modules)


def test_validation_runner_generates_utc_timestamp_index():
    frame = validation_runner._indicator_fixture()

    assert str(frame.index.tz) == "UTC"