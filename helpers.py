import pandas as pd
from datetime import datetime, timedelta

# def clean(data):
#     return data.apply(lambda row: pd.Series({
#             'blockchain': 'SUI',
#             'darAssetID': '???',  # TODO
#             'darAssetTicker': 'SUI',
#             'sedol': '???',       # TODO
#             'periodType': 'daily',
#             'rewardPeriodStartTime': (row['day_settled'] - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00'),
#             'rewardPeriodEndTime': row['day_settled'].strftime('%Y-%m-%d 00:00:00'),
#             'totalRewardQuantity': float(f"{float(row['epoch_rewards']):.6f}"),
#             'stakedQuantity': int(row['total_staked_near']),
#             'reserved1': None,
#             'reserved2': None,
#             'reserved3': None,
#             'reserved4': None,
#             'reserved5': None,
#             'reserved6': None,
#             'reserved7': None,
#             'reserved8': None,
#             'reserved9': None,
#             'reserved10': None
#         }),
#         axis=1
#     )


def clean(data):
    return data.apply(lambda row: format_row(row['date'], row['total_staked'] / 1_000_000_000, row['validator_rewards'] / 1_000_000_000), axis=1)

def format_row(date, current_staked, current_rewards):
    return pd.Series({
        'blockchain': 'Sui',
        'darAssetID': 'DAWFILV',
        'darAssetTicker': 'SUI',
        'sedol': 'BNKG9G7',
        'periodType': 'daily',
        'rewardPeriodStartTime': (date - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00'),
        'rewardPeriodEndTime': date.strftime('%Y-%m-%d 00:00:00'),
        'totalRewardQuantity': float(f"{float(current_rewards):.6f}"),
        'stakedQuantity': float(f"{float(current_staked):.6f}"),
        'reserved1': None,
        'reserved2': None,
        'reserved3': None,
        'reserved4': None,
        'reserved5': None,
        'reserved6': None,
        'reserved7': None,
        'reserved8': None,
        'reserved9': None,
        'reserved10': None
    })