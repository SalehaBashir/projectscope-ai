from app.estimation.rules import (
    get_complexity_multiplier,
    get_integration_multiplier,
    get_scale_multiplier,
)
from app.estimation.cost_rules import get_blended_rate, get_rate_for_task


class TestComplexityMultiplier:
    def test_low_medium_high(self):
        assert get_complexity_multiplier("low") == 1.0
        assert get_complexity_multiplier("medium") == 1.3
        assert get_complexity_multiplier("high") == 1.7

    def test_unknown_defaults_to_medium(self):
        assert get_complexity_multiplier("bogus") == 1.3


class TestIntegrationMultiplier:
    def test_single_integration_no_extra(self):
        assert get_integration_multiplier(1) == 1.0

    def test_multiple_integrations_scale(self):
        assert get_integration_multiplier(3) == 1.10

    def test_zero_integrations(self):
        assert get_integration_multiplier(0) == 1.0


class TestScaleMultiplier:
    def test_none(self):
        assert get_scale_multiplier("") == 1.0

    def test_million_scale_up(self):
        assert get_scale_multiplier("expect 1 million users") == 1.30

    def test_thousand(self):
        assert get_scale_multiplier("a few thousand") == 1.15

    def test_unknown_returns_one(self):
        assert get_scale_multiplier("a small beta") == 1.0


class TestCostRules:
    def test_get_rate_for_task_with_role(self):
        rates = {"r1": 20.0}
        assert get_rate_for_task("r1", rates, 10.0) == 20.0

    def test_get_rate_for_task_fallback_to_blended(self):
        assert get_rate_for_task("unknown", {}, 12.0) == 12.0

    def test_blended_rate(self):
        class R:
            def __init__(self, rate):
                self.hourly_rate = rate

        roles = [R(10), R(20), R(30)]
        assert get_blended_rate(roles) == 20.0

    def test_blended_rate_empty(self):
        assert get_blended_rate([]) == 0.0
