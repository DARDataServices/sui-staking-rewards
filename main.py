import requests
import json
from google.cloud import bigquery

# Sui RPC endpoint URL
SUI_RPC_URL = 'https://docs-demo.sui-mainnet.quiknode.pro/'
table_id = 'dar-dev-02.blockchain_sui.test'

def make_json_rpc_request(method, params=None):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params if params else []
    }
    try:
        response = requests.post(SUI_RPC_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        if 'error' in data:
            print(f"RPC Error: {data['error']}")
            return None
        return data.get('result', {})
    except requests.RequestException as e:
        print(f"Request Error: {e}")
        return None

def suix_getStakes(address):
    result = make_json_rpc_request('suix_getStakes', [address])
    return result[0].get('stakes') if result else None

def suix_getValidatorsApy():
    result = make_json_rpc_request('suix_getValidatorsApy')
    return result.get('apys'), int(result.get('epoch'))

def suix_getLatestSuiSystemState():
    result = make_json_rpc_request('suix_getLatestSuiSystemState')
    if result:
        epoch = result.get('epoch')
        total_stake = result.get('totalStake')
        epoch_start_timestamp = result.get('epochStartTimestampMs')
        active_validators = result.get('activeValidators')
    return epoch, total_stake, epoch_start_timestamp, active_validators

# collect total staked, current epoch, active validators



if __name__ == '__main__':
    epoch, total_stake, epoch_start_timestamp, active_validators = suix_getLatestSuiSystemState()
    active_validator_addresses = [validator.get('suiAddress') for validator in active_validators]

    print(f'Epoch {epoch} has {total_stake} staked Sui. The epoch started at {epoch_start_timestamp}.\nActive validators: {active_validator_addresses}')

    bq = bigquery.Client()

    row = {
        'epoch': epoch,
        'totalStake': total_stake,
        'epochStartTimestampMs': epoch_start_timestamp,
        'activeValidators': json.dumps(active_validator_addresses)
    }
    errors = bq.insert_rows_json(table_id, [row])

    if errors:
        print(f"Errors occurred while inserting row: {errors}")
    else:
        print('BigQuery insert complete - data successfully inserted.')

    # apys, current_epoch = suix_getValidatorsApy()
    # print(current_epoch)
    # print(epoch)
    # # active_validators = suix_getLatestSuiSystemState()
    # total_rewards = 0
    #
    # for validator in apys:
    #     address = validator.get('address')
    #     print(f'Address: {address}')
    #     if stakes := suix_getStakes(address):
    #         active_epochs = []
    #         for stake in stakes:
    #             stake_active_epoch = int(stake.get('stakeActiveEpoch'))
    #             active_epochs.append(stake_active_epoch)
    #
    #             if stake_active_epoch == (current_epoch - 1):
    #                 estimated_reward = stake.get('estimatedReward')
    #                 total_rewards += int(estimated_reward)
    #                 print(f'{stake_active_epoch} has estimated reward {estimated_reward}')
    #
    #         print(f'Address {address} active in epochs: {active_epochs}')
    #
    # print(f'Total rewards for {(current_epoch - 1)}: {total_rewards}')