# Copyright 2021 eprbell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from configuration import Configuration
from gain_loss import GainLoss
from in_transaction import InTransaction
from intra_transaction import IntraTransaction
from out_transaction import OutTransaction
from rp2_decimal import RP2Decimal
from rp2_error import RP2TypeError, RP2ValueError


class TestGainLoss(unittest.TestCase):
    _configuration: Configuration

    @classmethod
    def setUpClass(cls) -> None:
        TestGainLoss._configuration = Configuration("./config/test_data.config")

    def setUp(self) -> None:
        self.maxDiff = None

        self._in_buy = InTransaction(
            self._configuration,
            "2020-01-02T08:42:43.882Z",
            "B1",
            "Coinbase Pro",
            "Bob",
            "BuY",
            RP2Decimal("10000"),
            RP2Decimal("2.0002"),
            RP2Decimal("20"),
            RP2Decimal("20002"),
            RP2Decimal("20022"),
            unique_id=10,
        )
        self._in_buy2 = InTransaction(
            self._configuration,
            "2020-01-12T17:33:18Z",
            "B1",
            "Coinbase Pro",
            "Bob",
            "BuY",
            RP2Decimal("10500"),
            RP2Decimal("0.8"),
            RP2Decimal("10"),
            unique_id=11,
        )
        self._in_buy3 = InTransaction(
            self._configuration,
            "2020-04-27T03:28:47Z",
            "B1",
            "Coinbase Pro",
            "Bob",
            "BuY",
            RP2Decimal("1300"),
            RP2Decimal("1.5"),
            RP2Decimal("20"),
            unique_id=12,
        )
        self._in_earn = InTransaction(
            self._configuration,
            "2020-02-21T13:14:08 -00:04",
            "B1",
            "BlockFi",
            "Bob",
            "eaRn",
            RP2Decimal("11000"),
            RP2Decimal("0.1"),
            RP2Decimal("0"),
            unique_id=14,
        )
        self._out: OutTransaction = OutTransaction(
            self._configuration,
            "3/3/2020 3:59:59 -04:00",
            "B1",
            "Coinbase Pro",
            "Bob",
            "SELL",
            RP2Decimal("12000"),
            RP2Decimal("0.2"),
            RP2Decimal("0"),
            unique_id=20,
        )
        self._intra: IntraTransaction = IntraTransaction(
            self._configuration,
            "2021-03-10T11:18:58 -00:04",
            "B1",
            "Coinbase Pro",
            "Bob",
            "BlockFi",
            "Alice",
            RP2Decimal("12500.0"),
            RP2Decimal("0.4"),
            RP2Decimal("0.39"),
            unique_id=30,
        )

    def test_good_earn_gain_loss(self) -> None:
        flow: GainLoss = GainLoss(self._configuration, RP2Decimal("0.1"), self._in_earn, None)
        self.assertEqual(flow.crypto_amount, RP2Decimal("0.1"))
        self.assertEqual(flow.taxable_event, self._in_earn)
        self.assertEqual(flow.from_lot, None)
        self.assertEqual(flow.timestamp, flow.taxable_event.timestamp)
        self.assertEqual(flow.crypto_balance_change, RP2Decimal("0.1"))
        self.assertEqual(flow.taxable_event_usd_amount_with_fee_fraction, RP2Decimal("1100"))
        self.assertEqual(
            str(flow),
            """GainLoss:
  id=14->None
  crypto_amount=0.10000000
  usd_cost_basis=0.0000
  usd_gain=1100.0000
  is_long_term_capital_gains=False
  taxable_event_usd_amount_with_fee_fraction=1100.0000
  taxable_event_fraction_percentage=100.0000%
  taxable_event=InTransaction:
    id=14
    timestamp=2020-02-21 13:14:08.000000 -0004
    asset=B1
    exchange=BlockFi
    holder=Bob
    transaction_type=TransactionType.EARN
    spot_price=11000.0000
    crypto_in=0.10000000
    usd_fee=0.0000
    usd_in_no_fee=1100.0000
    usd_in_with_fee=1100.0000
    is_taxable=True
    usd_taxable_amount=1100.0000
  from_lot_usd_amount_with_fee_fraction=0.0000
  from_lot_fraction_percentage=0.0000%
  from_lot=None""",
        )
        self.assertEqual(
            repr(flow),
            "GainLoss(id='14->None', crypto_amount=0.10000000, usd_cost_basis=0.0000, usd_gain=1100.0000, is_long_term_capital_gains=False, taxable_event_usd_amount_with_fee_fraction=1100.0000, taxable_event_fraction_percentage=100.0000%, taxable_event=InTransaction(id='14', timestamp='2020-02-21 13:14:08.000000 -0004', asset='B1', exchange='BlockFi', holder='Bob', transaction_type=<TransactionType.EARN: 'earn'>, spot_price=11000.0000, crypto_in=0.10000000, usd_fee=0.0000, usd_in_no_fee=1100.0000, usd_in_with_fee=1100.0000, is_taxable=True, usd_taxable_amount=1100.0000), from_lot_usd_amount_with_fee_fraction=0.0000, from_lot_fraction_percentage=0.0000%, from_lot=None)",
        )

    def test_good_non_earn_gain_loss(self) -> None:
        flow: GainLoss = GainLoss(self._configuration, RP2Decimal("0.001"), self._intra, self._in_buy)
        self.assertEqual(flow.crypto_amount, RP2Decimal("0.001"))
        self.assertEqual(flow.taxable_event, self._intra)
        self.assertEqual(flow.from_lot, self._in_buy)
        self.assertEqual(flow.timestamp, flow.taxable_event.timestamp)
        self.assertEqual(flow.crypto_balance_change, RP2Decimal("0.001"))
        self.assertEqual(flow.taxable_event_usd_amount_with_fee_fraction, RP2Decimal("12.5"))
        self.assertEqual(
            str(flow),
            """GainLoss:
  id=30->10
  crypto_amount=0.00100000
  usd_cost_basis=10.0100
  usd_gain=2.4900
  is_long_term_capital_gains=True
  taxable_event_usd_amount_with_fee_fraction=12.5000
  taxable_event_fraction_percentage=10.0000%
  taxable_event=IntraTransaction:
    id=30
    timestamp=2021-03-10 11:18:58.000000 -0004
    asset=B1
    from_exchange=Coinbase Pro
    from_holder=Bob
    to_exchange=BlockFi
    to_holder=Alice
    transaction_type=TransactionType.MOVE
    spot_price=12500.0000
    crypto_sent=0.40000000
    crypto_received=0.39000000
    crypto_fee=0.01000000
    usd_fee=125.0000
    is_taxable=True
    usd_taxable_amount=125.0000
  from_lot_usd_amount_with_fee_fraction=10.0100
  from_lot_fraction_percentage=0.0500%
  from_lot=InTransaction:
    id=10
    timestamp=2020-01-02 08:42:43.882000 +0000
    asset=B1
    exchange=Coinbase Pro
    holder=Bob
    transaction_type=TransactionType.BUY
    spot_price=10000.0000
    crypto_in=2.00020000
    usd_fee=20.0000
    usd_in_no_fee=20002.0000
    usd_in_with_fee=20022.0000
    is_taxable=False
    usd_taxable_amount=0.0000""",
        )
        self.assertEqual(
            repr(flow),
            "GainLoss(id='30->10', crypto_amount=0.00100000, usd_cost_basis=10.0100, usd_gain=2.4900, is_long_term_capital_gains=True, taxable_event_usd_amount_with_fee_fraction=12.5000, taxable_event_fraction_percentage=10.0000%, taxable_event=IntraTransaction(id='30', timestamp='2021-03-10 11:18:58.000000 -0004', asset='B1', from_exchange='Coinbase Pro', from_holder='Bob', to_exchange='BlockFi', to_holder='Alice', transaction_type=<TransactionType.MOVE: 'move'>, spot_price=12500.0000, crypto_sent=0.40000000, crypto_received=0.39000000, crypto_fee=0.01000000, usd_fee=125.0000, is_taxable=True, usd_taxable_amount=125.0000), from_lot_usd_amount_with_fee_fraction=10.0100, from_lot_fraction_percentage=0.0500%, from_lot=InTransaction(id='10', timestamp='2020-01-02 08:42:43.882000 +0000', asset='B1', exchange='Coinbase Pro', holder='Bob', transaction_type=<TransactionType.BUY: 'buy'>, spot_price=10000.0000, crypto_in=2.00020000, usd_fee=20.0000, usd_in_no_fee=20002.0000, usd_in_with_fee=20022.0000, is_taxable=False, usd_taxable_amount=0.0000))",
        )

    def test_gain_loss_equality_and_hashing(self) -> None:
        gain_loss: GainLoss = GainLoss(self._configuration, RP2Decimal("0.001"), self._intra, self._in_buy)
        gain_loss2: GainLoss = GainLoss(self._configuration, RP2Decimal("0.001"), self._intra, self._in_buy)
        gain_loss3: GainLoss = GainLoss(self._configuration, RP2Decimal("0.001"), self._intra, self._in_buy2)
        gain_loss4: GainLoss = GainLoss(self._configuration, RP2Decimal("0.001"), self._out, self._in_buy)
        gain_loss5: GainLoss = GainLoss(self._configuration, RP2Decimal("0.001"), self._out, self._in_buy2)
        gain_loss6: GainLoss = GainLoss(self._configuration, RP2Decimal("0.1"), self._in_earn, None)
        self.assertEqual(gain_loss, gain_loss)
        self.assertEqual(gain_loss, gain_loss2)
        self.assertNotEqual(gain_loss, gain_loss3)
        self.assertNotEqual(gain_loss, gain_loss4)
        self.assertNotEqual(gain_loss, gain_loss5)
        self.assertNotEqual(gain_loss, gain_loss6)
        self.assertEqual(hash(gain_loss), hash(gain_loss))
        self.assertEqual(hash(gain_loss), hash(gain_loss2))
        # These hashes would only be equal in case of hash collision (possible but very unlikey).
        self.assertNotEqual(hash(gain_loss), hash(gain_loss3))
        self.assertNotEqual(hash(gain_loss), hash(gain_loss4))
        self.assertNotEqual(hash(gain_loss), hash(gain_loss5))
        self.assertNotEqual(hash(gain_loss), hash(gain_loss6))

    def test_bad_gain_loss(self) -> None:
        with self.assertRaisesRegex(RP2TypeError, "Parameter 'configuration' is not of type Configuration: .*"):
            # Bad configuration
            GainLoss(None, RP2Decimal("0.5"), self._in_earn, None)  # type: ignore

        with self.assertRaisesRegex(RP2TypeError, "Parameter 'configuration' is not of type Configuration: .*"):
            # Bad configuration
            GainLoss("config", RP2Decimal("0.5"), self._in_earn, None)  # type: ignore

        with self.assertRaisesRegex(RP2ValueError, "Parameter 'crypto_amount' has non-positive value .*"):
            # Bad amount
            GainLoss(self._configuration, RP2Decimal("-1"), self._out, None)

        with self.assertRaisesRegex(RP2TypeError, "Parameter 'crypto_amount' has non-Decimal value"):
            # Bad amount
            GainLoss(self._configuration, "0.5", self._in_earn, None)  # type: ignore

        with self.assertRaisesRegex(RP2TypeError, "Parameter 'taxable_event' is not of type AbstractTransaction: .*"):
            # Bad taxable event
            GainLoss(self._configuration, RP2Decimal("0.5"), None, self._in_buy)  # type: ignore

        with self.assertRaisesRegex(RP2TypeError, "Parameter 'taxable_event' is not of type AbstractTransaction: .*"):
            # Bad taxable event
            GainLoss(self._configuration, RP2Decimal("0.5"), "foobar", self._in_buy)  # type: ignore

        with self.assertRaisesRegex(RP2TypeError, "Parameter 'from_lot' is not of type InTransaction: "):
            # Bad from lot
            GainLoss(self._configuration, RP2Decimal("0.1"), self._out, 33)  # type: ignore

        with self.assertRaisesRegex(
            RP2TypeError,
            "from_lot must be None for EARN-typed taxable_events, instead it's foobar",
        ):
            # Bad from lot
            GainLoss(self._configuration, RP2Decimal("0.1"), self._in_earn, "foobar")  # type: ignore

        with self.assertRaisesRegex(RP2ValueError, "Parameter 'taxable_event' of class InTransaction is not taxable: .*"):
            # Taxable event not taxable
            GainLoss(self._configuration, RP2Decimal("0.2"), self._in_buy2, self._in_buy)

        with self.assertRaisesRegex(
            RP2ValueError,
            "crypto_amount must be == taxable_event.crypto_balance_change for EARN-typed taxable events, but they differ .* != .*",
        ):
            # Taxable event of type EARN: from_lot not None
            GainLoss(self._configuration, RP2Decimal("1.1"), self._in_earn, None)

        with self.assertRaisesRegex(
            RP2TypeError,
            "from_lot must be None for EARN-typed taxable_events, instead it's .*",
        ):
            # Taxable event of type EARN: from_lot not None
            GainLoss(self._configuration, RP2Decimal("0.1"), self._in_earn, self._in_buy2)

        with self.assertRaisesRegex(RP2TypeError, "from_lot must not be None for non-EARN-typed taxable_events"):
            # Taxable event not of type EARN: from lot None
            GainLoss(self._configuration, RP2Decimal("0.2"), self._out, None)

        with self.assertRaisesRegex(
            RP2ValueError,
            "crypto_amount .* is greater than taxable event amount .* or from-lot amount .*: ",
        ):
            # Taxable event of type EARN: from_lot not None
            GainLoss(self._configuration, RP2Decimal("2"), self._out, self._in_buy2)

        with self.assertRaisesRegex(RP2ValueError, "Timestamp of taxable_event <= timestamp of from_lot"):
            # Taxable event of type EARN: from_lot not None
            GainLoss(self._configuration, RP2Decimal("0.1"), self._out, self._in_buy3)

        with self.assertRaisesRegex(RP2ValueError, "taxable_event.asset .* != from_lot.asset .*"):
            # Mix different assets (B1 and B2) in the same GainLoss
            in_transaction: InTransaction = InTransaction(
                self._configuration,
                "2019-04-27T03:28:47Z",
                "B2",
                "Coinbase Pro",
                "Bob",
                "BuY",
                RP2Decimal("1300"),
                RP2Decimal("1.5"),
                RP2Decimal("20"),
                unique_id=11,
            )
            GainLoss(self._configuration, RP2Decimal("0.1"), self._out, in_transaction)


if __name__ == "__main__":
    unittest.main()
