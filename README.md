# Coupon Tracker Script

## Overview

This script is designed to interact with the Redcat Polygon Central API. It logs in to obtain bearer tokens for admin and member requests, creates a new coupon program, schedules a coupon for a specified member ID, and checks multiple store IDs to monitor when the coupon becomes available. It performs checks at 30-second intervals and logs all actions and errors in a `script.log` file.

## Features

- **Authentication**: Obtains bearer tokens for admin and member access.
- **Coupon Creation**: Creates a new coupon program with specified parameters.
- **Coupon Scheduling**: Schedules the created coupon for a specified member ID.
- **Monitoring**: Continuously checks store IDs to see when the coupon is available for use.
- **Logging**: Records all actions and errors in a log file for troubleshooting and verification.

## Requirements

- Python 3.x
- `requests` library
- `concurrent.futures` for threading
- `logging` for error handling

## Script Structure

1. **Get Bearer Tokens**: Log in and obtain tokens for authentication.
2. **Create Coupon**: Set up a new coupon program with specified details.
3. **Schedule Coupon**: Assign the created coupon to a member ID.
4. **Monitor Availability**: Continuously check the specified store IDs for coupon availability.

## Variables

- **client**: Client name for base URL and logging purposes.
- **admin_username**: Admin username for API access.
- **admin_password**: Admin password for API access.
- **member_username**: Member username for API access.
- **member_password**: Member password for API access.
- **member_id**: The ID of the member to whom the coupon is scheduled.
- **store_ids**: A list of store IDs to monitor for coupon availability.

## Usage

1. Update the necessary variables (client, admin_username, admin_password, member_username, member_password, member_id) in the `main()` function.
2. Run the script.

```bash
python coupon_tracker.py