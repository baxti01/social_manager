import json
import uuid

from django.contrib.auth import get_user_model, REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from social_core.actions import do_auth
from social_core.exceptions import AuthMissingParameter
from social_core.utils import parse_qs
from social_django.utils import psa

from api_auth.serializers import UserCreateSerializer, UserSerializer
from social_manager_api.exceptions import UniqueError
from social_manager_api.models import Account
from social_manager_api.services import AccountService

User = get_user_model()


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@never_cache
@api_view(["GET"])
@psa("/api/auth/complete/facebook")
def login_facebook(request, backend):
    account_name = request.GET.get('account_name', None)

    if not account_name or not isinstance(account_name, str):
        raise ValidationError(detail="account_name value is required query param. "
                                     "\n account_name value type must be str")
    account = None
    try:
        account = get_object_or_404(Account, name=account_name)
    except:
        pass

    if account:
        raise UniqueError(detail=f'Account name "{account_name}" already is exist.')

    state_name = request.backend.name + '_state'
    state = {'hash': request.backend.state_token(), 'account_name': account_name}
    request.backend.strategy.session_set(name=state_name, value=json.dumps(state))

    access_token = do_auth(request.backend, redirect_name=REDIRECT_FIELD_NAME)

    return access_token


@csrf_exempt
@api_view(["GET"])
@psa("/api/auth/complete/facebook")
def complete_facebook(request, backend, *args, **kwargs):
    state = json.loads(request.backend.get_session_state())
    account_name = state.get('account_name', uuid.uuid4())

    access_token = auth_complete(request.backend)

    data = {
        "name": account_name,
        "type": 'Instagram',
        "token": access_token,
    }

    account = AccountService.create_account(
        validated_data=data,
        user_id=request.user.pk
    )

    return HttpResponseRedirect(f'/api/accounts/{account.pk}')


def auth_complete(backend):
    backend.process_error(backend.data)
    if not backend.data.get('code'):
        raise AuthMissingParameter(backend, 'code')
    state = backend.validate_state()
    key, secret = backend.get_key_and_secret()
    response = backend.request(backend.access_token_url(), params={
        'client_id': key,
        'redirect_uri': backend.get_redirect_uri(state),
        'client_secret': secret,
        'code': backend.data['code']
    })
    # API v2.3 returns a JSON, according to the documents linked at issue
    # #592, but it seems that this needs to be enabled(?), otherwise the
    # usual querystring type response is returned.
    try:
        response = response.json()
    except ValueError:
        response = parse_qs(response.text)

    access_token = response['access_token']

    return access_token
