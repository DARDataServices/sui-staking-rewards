import os
import traceback

from PythonCore.aws_utils import upload_to_aws
from PythonCore.env_vars import get_env_var
from PythonCore.slack_alert import send_slack_alert
from PythonCore.bigquery_utils import BigQueryClient
from oauthlib.uri_validate import query
from pyarrow import timestamp
import ast
from clients.sui_client import SuiClient
from helpers import clean
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

    if bq.has_cycle_data(current_epoch):
        print(f"Data for current period already in {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
    else:
        row = {
            'epoch': current_epoch,
            'total_staked':sui_client.get_total_stake(current_epoch) ,
            'validator_rewards': 0,
            'active_validators': sui_client.get_active_validators(current_epoch),
            'timestamp': sui_client.get_settlement_time(current_epoch),
            'date': datetime.utcnow().strftime('%Y-%m-%d')
        }
        print(bq.insert_rows(row))

    query = f"SELECT validator_rewards FROM {PROJECT_ID}.{DATASET_ID}.{TABLE_ID} WHERE epoch = {current_epoch - 1}"
    prev_epoch_rewards = int(next(bq.query(query).result())[0])

    if prev_epoch_rewards != 0:
        print(f"Rewards for epoch {current_epoch - 1} already in {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}")
    else:
        # Get the active validators from the previous epoch
        query = f"SELECT active_validators FROM {PROJECT_ID}.{DATASET_ID}.{TABLE_ID} WHERE epoch = {current_epoch - 1}"
        result = next(bq.query(query).result())[0]
        validators = ast.literal_eval(result)

        prev_epoch_rewards = sui_client.get_staking_rewards_for_epoch(validators, current_epoch - 1)  # Get rewards for previous epoch
        print(f"Rewards found for epoch {current_epoch - 1}: {prev_epoch_rewards}")

        # Update BigQuery table with rewards value
        update_query = f"""
            UPDATE {PROJECT_ID}.{DATASET_ID}.{TABLE_ID}
            SET validator_rewards = {prev_epoch_rewards}
            WHERE epoch = {current_epoch - 1}
        """
        bq.query(update_query)

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