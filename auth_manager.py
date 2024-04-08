import requests
from custom_piazza_api.exceptions import AuthenticationError, NotAuthenticatedError, \
    RequestError


class AuthManager:

    def __init__(self):
        self.sessions = {}
        self.is_authenticated = False

    def test_sessions(self):
        print(self.sessions)

    def login(self, email, password):

        session = requests.Session()

        response = session.get('https://piazza.com/main/csrf_token')
        if response.text.upper().find('CSRF_TOKEN') == -1:
            raise AuthenticationError("Could not get CSRF token")
        csrf_token = response.text.translate({34: None, 59: None}).split("=")[1]

        response = session.post(
            'https://piazza.com/class',
            data=f'from=%2Fsignup&email={email}&password={password}&remember=on&csrf_token={csrf_token}'
        )

        # If non-successful http response, bail
        if response.status_code != 200:
            raise AuthenticationError(f"Could not authenticate.\n{response.text}")
        pos = response.text.upper().find('VAR ERROR_MSG')
        errorMsg = None
        if pos != -1:
            end = response.text[pos:].find(';')
            errorMsg = response.text[pos:pos + end].translate({34: None}).split('=')[1].strip()

        if errorMsg is not None:
            raise AuthenticationError(f"Could not authenticate.\n{errorMsg}")

        # store the success session into list
        self.sessions[email] = session

    def logout(self, email):
        if email not in self.sessions:
            raise ValueError(f"Could not find user {email}")
        self.sessions.pop(email)
