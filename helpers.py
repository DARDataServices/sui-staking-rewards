import pandas as pd
from datetime import datetime, timedelta

def clean(data):
    reversed_data = data.iloc[::-1].reset_index(drop=True)
    return reversed_data.apply(lambda row: format_row(row['date'], row['total_staked'], row['validator_rewards']), axis=1)

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


def calc_staking_rewards_for_epoch(validators, apys):
    if len(validators) != len(apys):
        raise ValueError(f"Length mismatch: validators={len(validators)}, apys={len(apys)}")

    merged_df = pd.merge(
        apys,
        validators,
        on=['validator', 'epoch'],
        # how='inner'
    )

    merged_df['apy'] = merged_df['apy'].astype(float)
    merged_df['stake'] = merged_df['stake'].astype(str).astype(float)  # Convert to string first to handle Decimal objects

    merged_df['daily_rate'] = merged_df['apy'] / 365
    merged_df['estimated_reward'] = merged_df['stake'] * merged_df['daily_rate']
    merged_df['stake_sui'] = merged_df['stake'] / 1_000_000_000
    merged_df['estimated_reward_sui'] = merged_df['estimated_reward'] / 1_000_000_000

    return merged_df['estimated_reward_sui'].sum()