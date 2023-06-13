import requests
import json

def main():
    print("work in progress")

    access_token = "{access-token}"
    ig_user_id = "{ig-user-id}"
    image_url = "{image-url}"
    caption = "{caption}"

    # Step 1: Create Container
    create_container_url = f"https://graph.facebook.com/v17.0/{ig_user_id}/media"
    create_container_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token
    }

    create_container_response = requests.post(create_container_url, create_container_payload)

    if create_container_response.status_code == 200:
        container_id = create_container_response.json().get('id')

        # Step 2: Publish Container
        publish_container_url = f"https://graph.facebook.com/v17.0/{ig_user_id}/media_publish"
        publish_container_payload = {
            "creation_id": container_id,
            "media_type": "STORIES",
            "access_token": access_token
        }

        publish_container_response = requests.post(publish_container_url, publish_container_payload)

        if publish_container_response.status_code == 200:
            media_id = publish_container_response.json().get('id')
            print(f"Story published successfully with media id: {media_id}")
        else:
            print(f"Failed to publish the container: {publish_container_response.text}")
    else:
        print(f"Failed to create the container: {create_container_response.text}")
