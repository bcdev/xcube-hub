import connexion

from xcube_hub import auth0, api
from xcube_hub.controllers.users import get_user_by_user_id
from xcube_hub.models import User
from xcube_hub.models.api_oauth_response import ApiOauthResponse
from xcube_hub.models.oauth_token import OauthToken


def oauth_token_post(body: OauthToken):
    """Get authorization token

    Get authorization token

    :param body: OauthToken
    :type body: dict | bytes

    :rtype: ApiOAuthResponse
    """
    if connexion.request.is_json:
        user = User.from_dict(body)
        token = auth0.get_management_token()
        user = get_user_by_user_id(user.username, token=token)
        app_metadata = user.result.app_metadata

        # try:
        #     client_id = app_metadata['client_id']
        #     client_secret = app_metadata['client_secret']
        # except KeyError as e:
        #     raise api.ApiError(400, "client id and secret required.")

        return ApiOauthResponse(access_token="fsvsdvdsv", token_type="bearer")
