import connexion
from xcube_hub.models.api_o_auth_response import ApiOAuthResponse  # noqa: E501
from xcube_hub.models.o_auth_token import OAuthToken  # noqa: E501


def oauth_token_post(body=None):  # noqa: E501
    """Get authorization token

    Get authorization token # noqa: E501

    :param body: OauthToken
    :type body: dict | bytes

    :rtype: ApiOAuthResponse
    """
    if connexion.request.is_json:
        body = OAuthToken.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
