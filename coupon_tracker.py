import requests
import uuid
import time
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
  filename="script.log",
  filemode='a',
  format='%(asctime)s - %(levelname)s - %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S',
  level=logging.INFO
)

def get_bearer_tokens(client, admin_username, admin_password, member_username, member_password):
  try:
    login_url = f""
    
    admin_response = requests.post(
      login_url,
      headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      json={
        "username": admin_username,
        "psw": admin_password,
        "auth_type": "U"
      }
    )
    admin_response.raise_for_status()
    admin_token = admin_response.json().get("token")
    
    member_response = requests.post(
      login_url,
      headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      json={
        "username": member_username,
        "psw": member_password,
        "tfa_pin": "",
        "tfa_token": None,
        "auth_type": "M",
        "save_session": "1",
        "next": "/"
      }
    )
    member_response.raise_for_status()
    member_token = member_response.json().get("token")

    if admin_token and member_token:
      logging.info(f"Login successful for client: {client} (Admin and Member)")
      return admin_token, member_token
    else:
      raise Exception("Login failed. No token received.")
  except Exception as e:
    log_error(admin_response if admin_token is None else member_response, f"Error during login: {e}")
    return None, None


def create_coupon(client, admin_token):
  try:
    url = f""
    program_name = f"Redcat test coupon #{str(uuid.uuid4())[:8]}" # Clipping the UUID as "ProgramName" has a charcter limit
    start_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    finish_date = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M")
    
    payload = {
      "DiscountType": "5",
      "Eligibility": "0",
      "ProgramName": program_name,
      "Description": "testing coupon issue",
      "DiscountAmount": "100",
      "DiscountUsage": "1",
      "StartDate": start_date,
      "FinishDate": finish_date,
      "TimeLockPeriod": "0",
      "PLUList": "1000958",
      "Amount": "0",
      "UseAlias": False,
      "Days": 127,
      "Visible": 2,
      "Type": 2
    }

    response = requests.post(
      url,
      headers={
        "Authorization": f"Bearer {admin_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      json=payload
    )
    response.raise_for_status()

    coupon_id = response.json().get("data", {}).get("ID")
    if coupon_id:
      logging.info(f"Coupon created successfully. Program Name: {program_name}, Coupon ID: {coupon_id}, Start Date: {start_date}")
      return coupon_id, program_name, start_date
    else:
      raise Exception("Coupon creation failed. No ID received.")
  except Exception as e:
    log_error(response, f"Error during coupon creation: {e}")
    return None, None, None


def schedule_coupon(client, admin_token, coupon_id, member_id):
  try:
    url = f""
    payload = {
      "Members": [member_id],
      "Multiple": False
    }
    response = requests.post(
      url,
      headers={
        "Authorization": f"Bearer {admin_token}",
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      json=payload
    )
    response.raise_for_status()

    logging.info(f"Coupon scheduled successfully for Coupon ID: {coupon_id}")
  except Exception as e:
    log_error(response, f"Error during coupon scheduling: {e}")


def monitor_coupon_availability(client, member_token, coupon_id, program_name, start_date, store_ids):
  polling_interval = 30 

  def check_store(store_id):
    try:
      url = f""
      while True:
        response = requests.get(
          url,
          headers={
            "Authorization": f"Bearer {member_token}",
            "Accept": "application/json"
          }
        )
        response.raise_for_status()

        coupons = response.json().get("data", [])
        for coupon in coupons:
          if coupon.get("ProgramID") == coupon_id:
            if coupon.get("Available") == 1:
              current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
              logging.info(f"Coupon is now available at Store ID {store_id}. Program Name: {program_name}, Coupon ID: {coupon_id}, Start Date: {start_date}, Available Time: {current_time}")
              return
            else:
              logging.info(f"Coupon not available yet at Store ID {store_id}. Coupon ID: {coupon_id}. Checking again in {polling_interval} seconds...")
        time.sleep(polling_interval)
    except Exception as e:
      log_error(response, f"Error during monitoring coupon availability for Store ID {store_id}: {e}")

  with ThreadPoolExecutor() as executor:
    executor.map(check_store, store_ids)


def log_error(response, error_message):
  """Logs error messages and the response JSON from the server"""
  logging.error(error_message)
  try:
    error_json = response.json()
    logging.error(f"Server error response: {error_json}")
  except Exception:
    logging.error("Failed to decode server error response")


def main():
  client = ""
  admin_username = f""
  admin_password = "" 
  member_username = ""  
  member_password = ""  
  member_id = 1
  store_ids = [116, 100, 284, 30, 119]

  logging.info("----- New Script Run Started -----")
  
  # Step 1: Log in and get the admin and member bearer tokens
  admin_token, member_token = get_bearer_tokens(client, admin_username, admin_password, member_username, member_password)
  if not admin_token or not member_token:
    logging.error("Exiting script due to failed login.")
    return

  # Step 2: Create a coupon and retrieve the coupon ID
  coupon_id, program_name, start_date = create_coupon(client, admin_token)
  if not coupon_id:
    logging.error("Exiting script due to failed coupon creation.")
    return

  # Step 3: Schedule the coupon
  schedule_coupon(client, admin_token, coupon_id, member_id)

  # Step 4: Monitor the coupon availability using the member bearer token
  monitor_coupon_availability(client, member_token, coupon_id, program_name, start_date, store_ids)

  logging.info("----- Script Run Ended -----\n")

if __name__ == "__main__":
  main()