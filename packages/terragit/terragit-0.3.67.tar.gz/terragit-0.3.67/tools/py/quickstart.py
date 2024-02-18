from json import dumps

from httplib2 import Http
import os
import requests
import gitlab
import sys

git_url="https://gitlab.allence.cloud"
if len(sys.argv) > 1:
    git_url = sys.argv[1]


CI_OPEN_MERGE_REQUESTS=os.environ.get('CI_OPEN_MERGE_REQUESTS').replace('!','/-/merge_requests/')
GITLAB_USER_NAME=os.environ.get('GITLAB_USER_NAME')

def main():
    """Hangouts Chat incoming webhook quickstart."""
    url = 'https://chat.googleapis.com/v1/spaces/AAAAfzftULU/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=msWWgyyHyeQeRVIAn5UmyME55BP8jtY9OsfXQSlAjyE%3D'
    bot_message = {
        'text': 'Hello '+str(GITLAB_USER_NAME) +' lance MR Gitlab CI CD !' +"https://gitlab.allence.cloud" +'/'+str(CI_OPEN_MERGE_REQUESTS)}
    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
    http_obj = Http()
    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )
    print(response)


if __name__ == '__main__':
    main()
