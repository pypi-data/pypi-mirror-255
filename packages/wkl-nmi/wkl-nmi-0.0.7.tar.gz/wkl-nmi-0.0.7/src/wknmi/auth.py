import google.auth.transport.requests
import google.oauth2.id_token


def get_id_token(audience):

    if audience == "http://127.0.0.1:8000":
        return ""

    """
    make_authorized_get_request makes a GET request to the specified HTTP endpoint
    by authenticating with the ID token obtained from the google-auth client library
    using the specified audience value.
    """

    # Cloud Run uses your service's hostname as the `audience` value
    # audience = 'https://my-cloud-run-service.run.app/'
    # For Cloud Run, `endpoint` is the URL (hostname + path) receiving the request
    # endpoint = 'https://my-cloud-run-service.run.app/my/awesome/url'

    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)

    return id_token


#     res =  requests.get(endpoint, headers={'Authorization': f'Bearer {id_token}'})

#     return res.json()


# result = make_authorized_get_request("https://nmi-server-orkrbzqvda-uc.a.run.app/subscriptions/by-user-id?org=testOrg4&user_id=1", "https://nmi-server-orkrbzqvda-uc.a.run.app")
# print(result)
