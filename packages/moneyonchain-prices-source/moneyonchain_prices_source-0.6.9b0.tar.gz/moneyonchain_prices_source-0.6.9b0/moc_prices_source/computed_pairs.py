import sys
from os.path import dirname, abspath
from inspect import getsource
from types   import LambdaType

base_dir = dirname(abspath(__file__))

bkpath   = sys.path[:]
sys.path.insert(0, dirname(base_dir), )

from moc_prices_source.engines.coins import \
    RIF_USDT, BTC_USD, MOC_BTC, RIF_BTC, ETH_BTC, MOC_USD, RIF_USD, RIF_USD_B, \
    RIF_USD_T, ETH_USD, USDT_USD_B, USDT_USD, BTC_USDT, BNB_USD, BNB_USDT, \
    USD_ARS_CCB, BTC_ARS, RIF_USD_TB, RIF_USD_WMTB, USD_COP_CCB, BTC_COP
from moc_prices_source.weighing import weighted_median
from moc_prices_source.cli import tabulate

sys.path = bkpath



computed_pairs = {
    MOC_USD: {
        'requirements': [MOC_BTC, BTC_USD],
        'formula': lambda moc_btc, btc_usd: moc_btc * btc_usd
    },
    RIF_USD_B: { # Passing through Bitcoin
        'requirements': [RIF_BTC, BTC_USD],
        'formula': lambda rif_btc, btc_usd: rif_btc * btc_usd
    },
    RIF_USD_TB: { # Passing through Tether & Bitcoin
        'requirements': [RIF_USDT, BTC_USD, BTC_USDT],
        'formula': lambda rif_usdt, btc_usd, btc_usdt: rif_usdt * btc_usd / btc_usdt
    },
    RIF_USD_WMTB: { # Passing through Tether & Bitcoin usinng weighted_median
        'requirements': [RIF_USDT, BTC_USD, BTC_USDT, RIF_BTC],
        'formula': lambda rif_usdt, btc_usd, btc_usdt, rif_btc: weighted_median(
                [(rif_usdt * btc_usd / btc_usdt), (rif_btc * btc_usd)],
                [0.75, 0.25])
    },    
    RIF_USD_T: { # Passing through Tether
        'requirements': [RIF_USDT, USDT_USD],
        'formula': lambda rif_usdt, usdt_usd: rif_usdt * usdt_usd
    },
    RIF_USD: { # Leave this as legacy
        'requirements': [RIF_BTC, BTC_USD],
        'formula': lambda rif_btc, btc_usd: rif_btc * btc_usd
    },
    ETH_USD: {
        'requirements': [ETH_BTC, BTC_USD],
        'formula': lambda eth_btc, btc_usd: eth_btc * btc_usd
    },
    USDT_USD_B: { # Passing through Bitcoin
        'requirements': [BTC_USD, BTC_USDT],
        'formula': lambda btc_usd, btc_usdt: btc_usd / btc_usdt
    },
    BNB_USD: {
        'requirements': [BNB_USDT, BTC_USD, BTC_USDT],
        'formula': lambda bnb_usdt, btc_usd, btc_usdt: bnb_usdt * btc_usd / btc_usdt
    },
    USD_ARS_CCB: {
        'requirements': [BTC_ARS, BTC_USD],
        'formula': lambda btc_ars, btc_usd: btc_ars / btc_usd
    },
    USD_COP_CCB: {
        'requirements': [BTC_COP, BTC_USD],
        'formula': lambda btc_cop, btc_usd: btc_cop / btc_usd
    },
}

for pair, data in computed_pairs.items():
    formula = data['formula']
    if isinstance(formula, LambdaType):
        formula_desc = ':'.join(getsource(formula).split('lambda')[-1].strip(
            ).split(':')[1:]).strip()
    else:
        formula_desc = repr(formula)
    data['formula_desc'] = '\n'.join(map(str.strip, formula_desc.split('\n')))


def show_computed_pairs_fromula():
    print()
    print("Computed pairs formula")
    print("-------- ----- -------")
    print("")
    table = [[str(pair), '=', data['formula_desc']] for pair,
             data in computed_pairs.items()]
    print(tabulate(table, tablefmt='plain'))
    print("")



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    show_computed_pairs_fromula()
