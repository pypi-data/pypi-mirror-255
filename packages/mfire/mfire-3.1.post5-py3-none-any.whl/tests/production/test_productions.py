from pathlib import Path

from mfire.production.productions import CDPProduction
from mfire.utils import JsonFile
from mfire.utils.date import Datetime
from tests.production.factories import CDPProductionFactory


class TestCDPProduction:
    inputs_dir: Path = Path(__file__).parent / "inputs"

    def test_init_dates(self):
        prod = CDPProductionFactory(
            DateBulletin="20230301T070000",
            DateProduction="20230301T060000",
            DateConfiguration="20230201",
        )
        assert prod.DateBulletin == Datetime(2023, 3, 1, 7)
        assert prod.DateProduction == Datetime(2023, 3, 1, 6)
        assert prod.DateConfiguration == Datetime(2023, 2, 1)

    def test_init_customer(self):
        prod = CDPProductionFactory(CustomerId=None, CustomerName=None)
        assert prod.CustomerId == "unknown"
        assert prod.CustomerName == "unknown"

    def test_hash(self):
        prod = CDPProductionFactory()
        assert prod.hash == "7fbede02"

    def test_dump(self, tmp_path, assert_equals_file):
        prod = CDPProductionFactory()
        prod.dump(tmp_path)

        assert_equals_file(tmp_path / "prom_production_id_7fbede02.json")

    def test_concat(self):
        assert CDPProduction.concat([]) is None

        prods = [CDPProductionFactory(), CDPProductionFactory()]
        result = CDPProduction.concat(prods)

        assert len(result.Components.Aleas) == 2
        assert len(result.Components.Text) == 2

    def test_integration(self, assert_equals_result):
        filename = self.inputs_dir / "output.json"
        cdp_prod = CDPProduction(**JsonFile(filename).load())
        assert_equals_result(cdp_prod)
