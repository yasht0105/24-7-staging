import time
import requests
import paramiko
import json

webhook_url = "https://hooks.slack.com/services/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"
icon_emoji = ":ghost:"

def send_slack_message(webhook_url, message, icon_emoji=":ghost:"):
    payload = {
        "text": message,
        "icon_emoji": icon_emoji
    }
    response = requests.post(webhook_url, data={"payload": json.dumps(payload)})

    if response.status_code != 200:
        print("Error sending Slack message: ", response.text)
    else:
        print("Slack message sent successfully!")

def check_stream_status(api_url):
    try:
        # Make the GET request to the API
        response = requests.get(api_url)
        response_data = response.json()

        # Extract the required fields
        status = response_data.get("status")
        webRTCViewerCount = response_data.get("webRTCViewerCount")

        # Check if the status is "broadcasting" and webRTCViewerCount is 1
        if status == "broadcasting" and webRTCViewerCount == 1:
            print("Stream is broadcasting with 1 WebRTC viewer.")
        else:
            message = "Stream is not broadcasting or there is no viewer"
            send_slack_message(webhook_url, message, icon_emoji)

        return True

    except requests.exceptions.RequestException as e:
        print(f"Error making the API call: {e}")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return False

def check_server_for_errors(server_ip, username, password):
    try:
        # SSH into the server
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server_ip, username=username, password=password)

        # Check for error files
        file_extensions = [".piderr", ".hprof"]
        error_files = []

        for ext in file_extensions:
            stdin, stdout, stderr = client.exec_command(f"ls /usr/local/antmedia/*{ext}")
            error_files.extend(stdout.readlines())

        if error_files:
            print("Error files found:")
            for file in error_files:
                print(file.strip())
            message = "The crash log or dump file is found on the server. Please check the logs"
            send_slack_message(webhook_url, message, icon_emoji)
        else:
            print("No error files found.")

    except paramiko.AuthenticationException as e:
        print(f"Authentication failed: {e}")
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    api_url = "http://ovh36.antmedia.io:5080/LiveApp/rest/v2/broadcasts/test"
    if check_stream_status(api_url):
        # Replace the following with server details
        server_ip = "54.36.113.133"
        username = "yash"
        password = "testtest"

        check_server_for_errors(server_ip, username, password)
