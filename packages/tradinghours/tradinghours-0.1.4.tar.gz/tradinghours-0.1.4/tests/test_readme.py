import os
import pytest

from tradinghours.market import Market, MarketHoliday
from tradinghours.currency import Currency, CurrencyHoliday
from tradinghours.schedule import ConcretePhase
from tradinghours.exceptions import NoAccess

from pprint import pprint
LEVEL = os.environ.get("API_KEY_LEVEL", "full").strip()

def test_market_list_all(level):

    for obj in Market.list_all():
        assert str(obj) == Market.get_string_format().format(**obj.data)


def test_get_by_finid_or_mic(level):
    # Get by either FinID or MIC
    market = Market.get('US.NYSE')
    assert str(market) == "Market: US.NYSE New York Stock Exchange America/New_York"
    market = Market.get('XNYS')
    assert str(market) == "Market: US.NYSE New York Stock Exchange America/New_York"


def test_follow_market(level):
    # AR.BCBA is permanently closed and replaced by AR.BYMA
    market = Market.get('AR.BCBA')
    original = Market.get('AR.BCBA', follow=False)

    assert market.fin_id == "AR.BYMA"
    assert original.fin_id == "AR.BCBA"


def test_market_list_holidays(level):
    holidays = Market.get('US.NYSE').list_holidays("2024-01-01", "2024-12-31")

    for obj in holidays[:3]:
        assert str(obj) == MarketHoliday.get_string_format().format(**obj.data)


@pytest.mark.xfail(LEVEL == "only_holidays", reason="No access", raises=NoAccess)
def test_generate_schedules(level):
    market = Market.get('XNYS')
    schedules = market.generate_schedules("2023-09-01", "2023-09-30")

    for obj in schedules:
        assert str(obj) == ConcretePhase.get_string_format().format(**obj.data)


@pytest.mark.xfail(LEVEL != "full", reason="No access", strict=True, raises=NoAccess)
def test_currencies_list_all(level):
    for obj in Currency.list_all():
        assert str(obj) == Currency.get_string_format().format(**obj.data)


@pytest.mark.xfail(LEVEL != "full", reason="No access", strict=True, raises=NoAccess)
def test_currency_list_holidays(level):
    currency = Currency.get('AUD')
    for obj in currency.list_holidays("2023-06-01", "2023-12-31"):
        assert str(obj) == CurrencyHoliday.get_string_format().format(**obj.data)



if __name__ == '__main__':
    nprint = lambda *s: print("\n", *s)

    print("Markets:")
    test_market_list_all()
    nprint("Markets:")
    test_get_by_finid_or_mic()
    nprint("Market.fin_ids:")
    test_follow_market()
    nprint("MarketHolidays:")
    test_market_list_holidays()
    nprint("Schedules:")
    test_generate_schedules()
    nprint("Currency:")
    test_currencies_list_all()
    nprint("CurrencyHolidays:")
    test_currency_list_holidays()