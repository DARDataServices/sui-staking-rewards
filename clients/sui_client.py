from PythonCore.node_utils import AbstractNodeClient
import requests
import json

class SuiClient(AbstractNodeClient):
    def __init__(self, rpc_url):
        super().__init__()
        self.rpc_provider = rpc_url

    def _make_rpc_request(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params if params else []
        }
        try:
            response = requests.post(self.rpc_provider, json=payload)
            response.raise_for_status()
            data = response.json()
            if 'error' in data:
                print(f"RPC Error: {data['error']}")
                return None
            return data.get('result', {})
        except requests.RequestException as e:
            print(f"Request Error: {e}")
            return None

    def get_staking_rewards_for_epoch(self, validators, epoch):
        epoch_rewards = 0

        for address in validators:
            response = self._make_rpc_request('suix_getStakes', [address])

            if response and isinstance(response, list):
                stakes = response[0].get('stakes', [])

                for stake in stakes:
                    if int(stake.get('stakeActiveEpoch')) == epoch:
                        epoch_rewards += int(stake.get('estimatedReward', 0))

        return epoch_rewards

    def get_settlement_time(self, epoch):
        result = self._make_rpc_request('suix_getLatestSuiSystemState')
        return result.get('epochStartTimestampMs') ## TODO is this correct?

    def get_current_epoch(self):
        result = self._make_rpc_request('suix_getLatestSuiSystemState')
        return int(result.get('epoch'))

    def get_total_stake(self, epoch):
        result = self._make_rpc_request('suix_getLatestSuiSystemState')
        return int(result.get('totalStake'))

    def get_active_validators(self, current_epoch):
        result = self._make_rpc_request('suix_getLatestSuiSystemState')
        active_validators = result.get('activeValidators')
        active_validators_list = [validator.get('suiAddress') for validator in active_validators]
        return json.dumps(active_validators_list)

    def get_staking_rewards(self, epoch):
        pass
