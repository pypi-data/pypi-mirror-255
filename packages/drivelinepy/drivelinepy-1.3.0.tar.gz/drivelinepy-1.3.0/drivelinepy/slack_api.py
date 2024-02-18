#================================================================================
# Author: Garrett York
# Date: 2024/02/01
# Description: Class for Slack API
#================================================================================

from .base_api_wrapper import BaseAPIWrapper
import os
import mimetypes

class SlackAPI(BaseAPIWrapper):

    #---------------------------------------------------------------------------
    # Constructor
    #---------------------------------------------------------------------------

    def __init__(self, token, base_url="https://slack.com/api/"):
        super().__init__(base_url)
        self.token = token

    #---------------------------------------------------------------------------
    # Method - Post Message
    #---------------------------------------------------------------------------

    def post_message(self, channel, text):
        """
        Posts a message to a specified channel on Slack.

        :param channel: The channel ID where the message will be posted.
        :param text: The text of the message to post.
        :return: The response from the Slack API.
        """
        self.logger.info("Entering post_message()")

        endpoint = "chat.postMessage"
        payload = {
            'channel': channel,
            'text': text
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {self.token}'
        }

        response = self.post(endpoint, data=payload, headers=headers)

        self.logger.info("Exiting post_message()")
        return response
    
    #---------------------------------------------------------------------------
    # Method - Post File + Message (optional)
    #---------------------------------------------------------------------------

    def upload_file(self, channel, file_absolute_path, text=None):

        """
        Uploads a file to a specified channel on Slack.

        This method attempts to upload a file to the specified Slack channel. It first checks if the file exists at the given path and then determines its MIME type for proper uploading. The file is then uploaded with an optional initial comment.

        :param channel: str
            The channel ID where the file will be uploaded.
        :param file_absolute_path: str
            The absolute path to the file to upload.
        :param text: str, optional
            An initial comment to add when uploading the file. Defaults to None. The API documentation refers to this parameter is initial_comment
            but it is referred to as text in this method to match the parameter name in the post_message method.

        :return: dict
            A dictionary response from the Slack API indicating the success or failure of the file upload.
        """
        self.logger.info("Entering upload_file()")

        if not os.path.exists(file_absolute_path):
            self.logger.error(f"File not found: {file_absolute_path}")
            return {"ok": False, "error": "file_not_found"}

        endpoint = "files.upload"

        # Attempt to determine the MIME type of the file based on its extension. 
        # The `guess_type` function returns a tuple (MIME type, encoding), 
        # where we are only interested in the MIME type. The underscore (_) 
        # is used to ignore the encoding part of the returned tuple.
        
        mime_type, _ = mimetypes.guess_type(file_absolute_path)
        mime_type = mime_type or 'application/octet-stream'

        try:
            with open(file_absolute_path, 'rb') as file_content:
                files = [('file', (os.path.basename(file_absolute_path), file_content, mime_type))]
                payload = {'channels': channel, 'initial_comment': text}
                headers = {'Authorization': f'Bearer {self.token}'}
                response = self.post(endpoint, headers=headers, data=payload, files=files)
        except Exception as e:
            self.logger.error(f"Error uploading file: {e}")
            return {"ok": False, "error": str(e)}

        self.logger.info("Exiting upload_file()")
        return response
