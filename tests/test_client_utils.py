import random

from pygraphql.client.utils import RandomExponentialSleep


def test_RandomExponentialSleep():
    random.seed(42)
    gen = RandomExponentialSleep(
        multiplier=1,
        max_sleep=300,
        exp_base=2,
        min_sleep=0,
    )

    assert gen(1) == 1.2788535969157675
    assert gen(2) == 0.10004302089066774
    assert gen(3) == 2.200234546952954
