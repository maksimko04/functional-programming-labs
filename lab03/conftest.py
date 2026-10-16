import pytest
from model import Coverage, Policy, make_policy


@pytest.fixture
def policy() -> Policy:
    return make_policy(
        1,
        "Ivan Petrenko",
        (Coverage("car", 10_000.0, 0.05), Coverage("health", 5_000.0, 0.02)),
        frozenset({"low"}),
        source="web",
        agent="A-7",
    )
