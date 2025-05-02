import os
import traceback

from PythonCore.aws_utils import upload_to_aws
from PythonCore.env_vars import get_env_var
from PythonCore.slack_alert import send_slack_alert
from PythonCore.bigquery_utils import BigQueryClient

from clients.sui_client import SuiClient
from helpers import clean, calc_staking_rewards_for_epoch
from datetime import datetime

PROJECT_ID = get_env_var("PROJECT_ID")
DATASET_ID = get_env_var('DATASET_ID')
TABLE_ID = get_env_var('TABLE_ID')
RPC_URL = get_env_var('RPC_URL')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME')
# AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")

def main():
    bq = BigQueryClient(PROJECT_ID, DATASET_ID, TABLE_ID)
    sui_client = SuiClient(RPC_URL)

    current_epoch = sui_client.get_current_epoch()
    print(f"Current epoch: {current_epoch}")

    if bq.has_cycle_data(current_epoch):
        print(f"Data for current epoch {current_epoch} already in {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
    else:
        apys = sui_client.get_validator_apys()
        validators = sui_client.get_active_validators()
        # TODO Store APY and Validators for record keeping purposes ?
        row = {
            'epoch': current_epoch,
            'total_staked':sui_client.get_total_stake(current_epoch),
            'validator_rewards': calc_staking_rewards_for_epoch(validators, apys),
            'timestamp': sui_client.get_settlement_time(current_epoch),
            'date': datetime.utcnow().strftime('%Y-%m-%d')
        }
        print(bq.insert_rows(row))


    data = bq.fetch_historical_data()
    file = clean(data)
    bq.upload_to_s3(file, GCS_BUCKET_NAME)
    # send_slack_alert(bq.upload_to_s3(file, GCS_BUCKET_NAME))
    # send_slack_alert(upload_to_aws(file, get_env_var('AWS_BUCKET_NAME')))
    print("Done.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        send_slack_alert(f"Error collecting SUI rewards: {str(e)}\nTraceback: {traceback.format_exc()}")