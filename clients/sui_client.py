from PythonCore.node_utils import AbstractNodeClient
import requests
import pandas as pd

class SuiClient(AbstractNodeClient):
    def __init__(self, rpc_url):
        super().__init__()
        self.rpc_provider = rpc_url

    def _make_rpc_request(self, method, params=None):
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
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

    def get_settlement_time(self, epoch):
        result = self._make_rpc_request('suix_getLatestSuiSystemState')
        return result.get('epochStartTimestampMs')

    def get_current_epoch(self):
        result = self._make_rpc_request('suix_getLatestSuiSystemState')
        return int(result.get('epoch'))

    def get_total_stake(self, epoch):
        result = self._make_rpc_request('suix_getLatestSuiSystemState')
        return int(result.get('totalStake')) / 1_000_000_000

    def get_active_validators(self):
        result = self._make_rpc_request('suix_getLatestSuiSystemState')

        active_validators = result.get('activeValidators')
        current_epoch = int(result.get('epoch'))

        rows = []
        for validator_data in active_validators:
            row = {
                "validator": validator_data["suiAddress"],
                "stake": float(validator_data["stakingPoolSuiBalance"]),
                "epoch": current_epoch,
            }
            rows.append(row)

        return pd.DataFrame(rows)

    def get_validator_apys(self):
        result = self._make_rpc_request('suix_getValidatorsApy')

        validators_apy_data  = result.get('apys')
        current_epoch = int(result.get('epoch'))

        rows = []
        for validator_data in validators_apy_data:
            row = {
                "validator": validator_data["address"],
                "apy": float(validator_data["apy"]),
                "epoch": current_epoch
            }
            rows.append(row)

        return pd.DataFrame(rows)


    def get_staking_rewards(self, epoch):
        pass
