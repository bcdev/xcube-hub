from xcube_hub import api
from xcube_hub.core import oauth
from xcube_hub.typedefs import JsonObject


def oauth_token_post(body: JsonObject):
    """Get authorization token

    Get authorization token

    :param body: OauthToken
    :type body: dict | bytes

    :rtype: ApiOAuthResponse
    """

    try:

        encoded_jwt = oauth.get_token(body)

        return dict(access_token=encoded_jwt, token_type="bearer")
    except api.ApiError as e:
        return e.response
