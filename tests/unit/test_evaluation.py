import pytest

from pixelguard.evaluation import calculate_metrics, exact_match


def test_exact_match_detects_identical_bytes() -> None:
    content = b"same file content"

    assert exact_match(content, content) is True


def test_exact_match_rejects_different_bytes() -> None:
    assert exact_match(b"file A", b"file B") is False


def test_metrics_calculate_binary_classification_scores() -> None:
    result = calculate_metrics(
        expected=[True, True, False, False],
        predicted=[True, False, True, False],
    )

    assert result["true_positives"] == 1
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 1
    assert result["true_negatives"] == 1
    assert result["precision"] == pytest.approx(0.5)
    assert result["recall"] == pytest.approx(0.5)
    assert result["f1"] == pytest.approx(0.5)


def test_metrics_reject_unequal_lengths() -> None:
    with pytest.raises(ValueError, match="equal lengths"):
        calculate_metrics([True], [True, False])


def test_metrics_reject_empty_dataset() -> None:
    with pytest.raises(ValueError, match="at least one"):
        calculate_metrics([], [])
