import logging
import re
from datetime import datetime, timedelta
from http.cookies import SimpleCookie

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TransactionTestCase, modify_settings, override_settings
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import jwt
from freezegun import freeze_time

from pfx.pfxcore.test import APIClient, TestAssertMixin, get_auth_cookie
from tests.models import User

logger = logging.getLogger(__name__)


class AuthAPITest(TestAssertMixin, TransactionTestCase):

    def setUp(self):
        self.client = APIClient(default_locale='en')
        self.cookie_client = APIClient(default_locale='en', with_cookie=True)
        self.user1 = User.objects.create_user(
            username='jrr.tolkien',
            email="jrr.tolkien@oxford.com",
            password='RIGHT PASSWORD',
            first_name='John Ronald Reuel',
            last_name='Tolkien',
        )

    def test_invalid_login(self):
        response = self.client.post(
            '/api/auth/login', {
                'username': 'jrr.tolkien',
                'password': 'WRONG PASSWORD'})
        self.assertRC(response, 401)

    def test_emtpy_login(self):
        response = self.client.post(
            '/api/auth/login', {})
        self.assertRC(response, 401)

    @override_settings(PFX_TOKEN_SHORT_VALIDITY={'minutes': 30})
    def test_valid_login(self):
        response = self.client.post(
            '/api/auth/login', {
                'username': 'jrr.tolkien',
                'password': 'RIGHT PASSWORD'})

        self.assertRC(response, 200)
        decoded = jwt.decode(
            response.json_content['token'], settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)
        self.assertTrue(
            datetime.utcnow() + timedelta(minutes=25) <
            datetime.utcfromtimestamp(decoded['exp'])
            < datetime.utcnow() + timedelta(minutes=35))

    @override_settings(PFX_TOKEN_LONG_VALIDITY={'minutes': 60})
    def test_valid_login_remember_me(self):
        response = self.client.post(
            '/api/auth/login', {
                'username': 'jrr.tolkien',
                'password': 'RIGHT PASSWORD',
                'remember_me': True})

        self.assertRC(response, 200)
        decoded = jwt.decode(
            response.json_content['token'], settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)
        self.assertTrue(
            datetime.utcnow() + timedelta(minutes=55) <
            datetime.utcfromtimestamp(decoded['exp'])
            < datetime.utcnow() + timedelta(minutes=65))

    @override_settings(PFX_TOKEN_SHORT_VALIDITY={'minutes': 30})
    def test_valid_login_with_cookie(self):
        response = self.client.post(
            '/api/auth/login?mode=cookie', {
                'username': 'jrr.tolkien',
                'password': 'RIGHT PASSWORD'})

        cookie = get_auth_cookie(response)
        regex = r".*token=([\w\._-]*);.*"
        token = re.findall(regex, str(cookie))[0]

        # The cookie should be a session cookie
        # (removed when browser is closed)
        regex = r".*expires=([^;]*);.*"
        expires = re.findall(regex, str(cookie))
        regex = r".*Max-Age=([^;]*);.*"
        max_age = re.findall(regex, str(cookie))
        self.assertEqual(len(expires), 0)
        self.assertEqual(len(max_age), 0)

        self.assertRC(response, 200)
        decoded = jwt.decode(
            token, settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)

        # token expires in 30 minutes +/- 5 minutes.
        self.assertTrue(
            datetime.utcnow() + timedelta(minutes=25) <
            datetime.utcfromtimestamp(decoded['exp'])
            < datetime.utcnow() + timedelta(minutes=35))

    @override_settings(PFX_TOKEN_LONG_VALIDITY={'minutes': 60})
    def test_valid_login_with_cookie_remember_me(self):
        response = self.client.post(
            '/api/auth/login?mode=cookie', {
                'username': 'jrr.tolkien',
                'password': 'RIGHT PASSWORD',
                'remember_me': 'true'})

        cookie = get_auth_cookie(response)

        regex = r".*token=([\w\._-]*);.*"
        token = re.findall(regex, str(cookie))[0]

        regex = r".*expires=([^;]*);.*"
        expires = re.findall(regex, str(cookie))[0]
        d = datetime.strptime(expires, '%a, %d %b %Y %H:%M:%S %Z')

        regex = r".*Max-Age=([^;]*);.*"
        max_age = re.findall(regex, str(cookie))[0]

        # cookie expires in 60 minutes +/- 5 minutes.
        self.assertTrue(
            datetime.utcnow() + timedelta(minutes=55) <
            d < datetime.utcnow() + timedelta(minutes=65))
        self.assertEqual(int(max_age), 3600)

        self.assertRC(response, 200)
        decoded = jwt.decode(
            token, settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)

        # token expires in 60 minutes +/- 5 minutes.
        self.assertTrue(
            datetime.utcnow() + timedelta(minutes=55) <
            datetime.utcfromtimestamp(decoded['exp'])
            < datetime.utcnow() + timedelta(minutes=65))

    def test_logout(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.get('/api/auth/logout')
        self.assertRC(response, 200)
        cookie = [v for k, v in response.client.cookies.items()
                  if k == 'token'][0]
        regex = r".*token=([\"\"]*);.*"
        token = re.findall(regex, str(cookie))[0]
        self.assertEqual(token, '""')

    @override_settings(
        PFX_COOKIE_DOMAIN='example.com',
        PFX_COOKIE_SECURE='True',
        PFX_COOKIE_SAMESITE='Lax'
    )
    def test_logout_with_cookie_params(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.get('/api/auth/logout')
        self.assertRC(response, 200)
        cookie = [v for k, v in response.client.cookies.items()
                  if k == 'token'][0]

        regex = r"token=([\"\"]*);"
        token = re.findall(regex, str(cookie))[0]
        self.assertEqual(token, '""')

        regex = r"Domain=(.*?);"
        domain = re.findall(regex, str(cookie))[0]
        self.assertEqual(domain, 'example.com')

        regex = r"SameSite=(.*)"
        sameSite = re.findall(regex, str(cookie))[0]
        self.assertEqual(sameSite, 'Lax')

    def test_valid_change_password(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': 'NEW RIGHT PASSWORD'})
        self.assertRC(response, 200)

        self.cookie_client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'NEW RIGHT PASSWORD',
                'new_password': 'RIGHT PASSWORD'})
        self.assertRC(response, 200)

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME':
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator',
    }, {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    }])
    def test_change_password_validation(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': 'jrr'})
        self.assertRC(response, 422)
        self.assertJE(response, 'new_password.@0',
                      "The password is too similar to the username.")
        self.assertJE(response, 'new_password.@1',
                      "This password is too short. "
                      "It must contain at least 8 characters.")
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': '9ashff8za-@#asd'})
        self.assertRC(response, 200)

    def test_invalid_change_password(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')

        # Wrong old password
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'WRONG PASSWORD',
                'new_password': 'NEVER APPLIED PASSWORD'})
        self.assertRC(response, 422)
        self.assertJE(response, "old_password.@0", "Incorrect password")

    def test_empty_change_password(self):
        self.client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')
        response = self.client.post(
            '/api/auth/change-password', {})
        self.assertRC(response, 422)
        self.assertJE(response, "old_password.@0", "Incorrect password")
        self.assertJE(
            response, "new_password.@0", "Empty password is not allowed")

        # No new password
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD'})
        self.assertRC(response, 422)
        self.assertJE(
            response, "new_password.@0", "Empty password is not allowed")

        # Empty new password
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': ''})
        self.assertRC(response, 422)
        self.assertJE(
            response, "new_password.@0", "Empty password is not allowed")

        # None new password
        response = self.client.post(
            '/api/auth/change-password', {
                'old_password': 'RIGHT PASSWORD',
                'new_password': None})
        self.assertRC(response, 422)
        self.assertJE(
            response, "new_password.@0", "Empty password is not allowed")

    @override_settings(
        PFX_TOKEN_SHORT_VALIDITY={'minutes': 30},
        PFX_COOKIE_DOMAIN='example.com')
    def test_valid_cookie_token_with_domain(self):
        self.cookie_client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')

        regex = r".*Domain=([^;]*);.*"
        domain = re.findall(regex, str(self.cookie_client.auth_cookie))[0]
        self.assertEqual(domain, 'example.com')

        regex = r"\s(Secure)\s*"
        secure = re.findall(regex, str(self.cookie_client.auth_cookie))[0]
        self.assertEqual(secure, "Secure")  # default value

        regex = r".*SameSite=([^;]*).*"
        samesite = re.findall(regex, str(self.cookie_client.auth_cookie))[0]
        self.assertEqual(samesite, "None")  # default value

        response = self.cookie_client.get(
            '/api/private/authors')
        self.assertRC(response, 200)

    @override_settings(
        PFX_COOKIE_DOMAIN='example.com',
        PFX_COOKIE_SECURE=False,
        PFX_COOKIE_SAMESITE='Lax')
    def test_valid_cookie_token_with_domain_same_site_insecure(self):
        self.cookie_client.login(
            username='jrr.tolkien',
            password='RIGHT PASSWORD')

        regex = r".*Domain=([^;]*);.*"
        domain = re.findall(regex, str(self.cookie_client.auth_cookie))[0]
        self.assertEqual(domain, 'example.com')

        regex = r"\s(Secure)\s*"
        self.assertEqual(
            len(re.findall(regex, str(self.cookie_client.auth_cookie))), 0)

        regex = r".*SameSite=([^;]*).*"
        samesite = re.findall(regex, str(self.cookie_client.auth_cookie))[0]
        self.assertEqual(samesite, "Lax")

        response = self.cookie_client.get(
            '/api/private/authors')
        self.assertRC(response, 200)

    @override_settings(PFX_TOKEN_SHORT_VALIDITY={'hours': 4})
    def test_expired_token(self):
        with freeze_time("2023-05-01 08:00:00"):
            self.client.login(
                username='jrr.tolkien',
                password='RIGHT PASSWORD')
        with freeze_time("2023-05-01 12:01:00"):
            response = self.client.get(
                '/api/private/authors')
            self.assertRC(response, 401)

    @override_settings(PFX_TOKEN_LONG_VALIDITY={'days': 2})
    def test_expired_cookie_with_expired_token(self):

        with freeze_time("2023-05-01 08:00:00"):
            self.cookie_client.login(
                username='jrr.tolkien',
                password='RIGHT PASSWORD',
                remember_me=True)
        with freeze_time("2023-05-04 08:00:00"):
            response = self.cookie_client.get(
                '/api/private/authors')
            self.assertRC(response, 401)
            self.assertEqual(
                str(get_auth_cookie(response)),
                'Set-Cookie: token=""; expires=Thu, 01 Jan 1970 00:00:00 GMT; '
                'Max-Age=0; Path=/; SameSite=None; Secure')

    def test_invalid_auth_header(self):
        logging.disable(logging.CRITICAL)
        response = self.client.get(
            '/api/private/authors',
            HTTP_AUTHORIZATION='Beer here',
            content_type='application/json')
        logging.disable(logging.NOTSET)
        self.assertRC(response, 401)

    def test_valid_token_with_invalid_user(self):
        user = User.objects.create_user(
            username='invisible.man',
            email="iv@invisible.com",
            password='RIGHT PASSWORD',
            first_name='Peter',
            last_name='Invisible',
        )
        self.client.login(
            username='invisible.man',
            password='RIGHT PASSWORD')
        user.delete()
        response = self.client.get(
            '/api/private/authors')
        self.assertRC(response, 401)

    def test_valid_cookie_with_invalid_user(self):
        user = User.objects.create_user(
            username='invisible.man',
            email="iv@invisible.com",
            password='RIGHT PASSWORD',
            first_name='Peter',
            last_name='Invisible',
        )
        self.cookie_client.login(
            username='invisible.man',
            password='RIGHT PASSWORD')
        user.delete()
        response = self.cookie_client.get(
            '/api/private/authors')
        self.assertRC(response, 401)
        self.assertEqual(
            str(get_auth_cookie(response)),
            'Set-Cookie: token=""; expires=Thu, 01 Jan 1970 00:00:00 GMT; '
            'Max-Age=0; Path=/; SameSite=None; Secure')

    def test_valid_cookie_with_invalid_user_and_public_service(self):
        user = User.objects.create_user(
            username='invisible.man',
            email="iv@invisible.com",
            password='RIGHT PASSWORD',
            first_name='Peter',
            last_name='Invisible',
        )
        self.cookie_client.login(
            username='invisible.man',
            password='RIGHT PASSWORD')
        user.delete()
        response = self.cookie_client.get(
            '/api/books')
        self.assertRC(response, 200)
        self.assertEqual(
            str(get_auth_cookie(response)),
            'Set-Cookie: token=""; expires=Thu, 01 Jan 1970 00:00:00 GMT; '
            'Max-Age=0; Path=/; SameSite=None; Secure')

    def test_invalid_token(self):
        token = jwt.encode(
            {'pfx_user_pk': 1}, "A WRONG SECRET", algorithm="HS256")
        logging.disable(logging.CRITICAL)
        response = self.client.get(
            '/api/private/authors',
            HTTP_AUTHORIZATION='Bearer ' + token,
            content_type='application/json')
        logging.disable(logging.NOTSET)
        self.assertRC(response, 401)

    def test_invalid_token_with_public_service(self):
        token = jwt.encode(
            {'pfx_user_pk': 1}, "A WRONG SECRET", algorithm="HS256")
        logging.disable(logging.CRITICAL)
        response = self.client.get(
            '/api/books',
            HTTP_AUTHORIZATION='Bearer ' + token,
            content_type='application/json')
        logging.disable(logging.NOTSET)
        self.assertRC(response, 200)

    def test_invalid_cookie_token(self):
        token = jwt.encode(
            {'pfx_user_pk': 1}, "A WRONG SECRET", algorithm="HS256")
        logging.disable(logging.CRITICAL)
        self.client.cookies = SimpleCookie({'token': token})
        response = self.client.get(
            '/api/private/authors',
            content_type='application/json')
        logging.disable(logging.NOTSET)
        self.assertRC(response, 401)
        self.assertEqual(
            str(get_auth_cookie(response)),
            'Set-Cookie: token=""; expires=Thu, 01 Jan 1970 00:00:00 GMT; '
            'Max-Age=0; Path=/; SameSite=None; Secure')

    def test_invalid_cookie_token_with_public_service(self):
        token = jwt.encode(
            {'pfx_user_pk': 1}, "A WRONG SECRET", algorithm="HS256")
        logging.disable(logging.CRITICAL)
        self.client.cookies = SimpleCookie({'token': token})
        response = self.client.get(
            '/api/books',
            content_type='application/json')
        logging.disable(logging.NOTSET)
        self.assertRC(response, 200)
        self.assertEqual(
            str(get_auth_cookie(response)),
            'Set-Cookie: token=""; expires=Thu, 01 Jan 1970 00:00:00 GMT; '
            'Max-Age=0; Path=/; SameSite=None; Secure')

    def test_signup(self):
        # Try to create with an existing username
        response = self.client.post(
            '/api/auth/signup', {
                'username': 'jrr.tolkien',
                'email': "jrr.tolkien@oxford.com",
                'first_name': 'John Ronald Reuel',
                'last_name': 'Tolkien',
            })

        self.assertRC(response, 422)
        self.assertEqual(response.json_content['username'],
                         ['A user with that username already exists.'])

        # Then create another valid user
        response = self.client.post(
            '/api/auth/signup', {
                'username': 'isaac.asimov',
                'email': 'isaac.asimov@bu.edu',
                'first_name': 'Isaac',
                'last_name': 'Asimov',
            })

        self.assertRC(response, 200)

        # Must send a welcome email
        self.assertEqual(
            mail.outbox[0].subject,
            f'Welcome on {settings.PFX_SITE_NAME}')

        self.client.logout()

        # Test that the token and uid are valid.
        regex = r"token=(.*)&uidb64=(.*)"
        token, uidb64 = re.findall(regex, mail.outbox[0].body)[0]
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uidb64,
                'password': 'test'
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'message', 'password updated successfully')

    def test_empty_signup(self):
        # Try empty signup
        response = self.client.post(
            '/api/auth/signup', {})
        self.assertRC(response, 422)
        self.assertJE(response, 'username.@0', 'This field cannot be blank.')

    def test_forgotten_password(self):
        # Try with an nonexistent email
        response = self.client.post(
            '/api/auth/forgotten-password', {
                'email': 'isaac.asimov@bu.edu',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'message',
                      'If the email address you entered is correct, '
                      'you will receive an email from us with '
                      'instructions to reset your password.')

        # Then try with a valid email
        response = self.client.post(
            '/api/auth/forgotten-password', {
                'email': 'jrr.tolkien@oxford.com',
            })

        self.assertRC(response, 200)
        self.assertJE(response, 'message',
                      'If the email address you entered is correct, '
                      'you will receive an email from us with '
                      'instructions to reset your password.')

        # Must send a reset password email
        self.assertEqual(
            mail.outbox[0].subject,
            f'Password reset on {settings.PFX_SITE_NAME}')

        self.client.logout()

        # Test that the token and uid are valid.
        regex = r"token=(.*)&uidb64=(.*)"
        token, uidb64 = re.findall(regex, mail.outbox[0].body)[0]
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uidb64,
                'password': 'test'
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'message', 'password updated successfully')

    def test_empty_email_forgotten_password(self):
        # Try with an empty body
        response = self.client.post(
            '/api/auth/forgotten-password', {
            })
        self.assertRC(response, 422)
        self.assertJE(response, 'email.@0', 'Enter a valid email address.')

        # Try with an empty email address
        response = self.client.post(
            '/api/auth/forgotten-password', {
                'email': '',
            })
        self.assertRC(response, 422)
        self.assertJE(response, 'email.@0', 'Enter a valid email address.')

    def test_wrong_email_forgotten_password(self):
        # Try with an invalid email address
        response = self.client.post(
            '/api/auth/forgotten-password', {
                'email': 'jrr.tolkien',
            })
        self.assertRC(response, 422)
        self.assertJE(response, 'email.@0', 'Enter a valid email address.')

        # Try with another invalid email address
        response = self.client.post(
            '/api/auth/forgotten-password', {
                'email': '@bluestar.solutions',
            })
        self.assertRC(response, 422)
        self.assertJE(response, 'email.@0', 'Enter a valid email address.')

    def test_validate_user_token(self):
        # Try with a wrong token and uid
        response = self.client.post(
            '/api/auth/validate-user-token', {
                'token': 'WRONG TOKEN',
                'uidb64': 'WRONG UID'
            })

        self.assertRC(response, 422)
        self.assertJE(response, '__all__.@0', "User or token is invalid")

        # Then try with a valid token and uid
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/validate-user-token', {
                'token': token,
                'uidb64': uid
            })
        self.assertRC(response, 200)
        self.assertJE(response, '__all__.@0', "User and token are valid")

    def test_set_password(self):
        # Try with a wrong token and uid
        response = self.client.post(
            '/api/auth/set-password', {
                'token': 'WRONG TOKEN',
                'uidb64': 'WRONG UID',
                'password': 'NEW PASSWORD',
            })

        self.assertRC(response, 401)

        # Then try with a valid token and uid
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'NEW PASSWORD',
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'message', "password updated successfully")

    @override_settings(AUTH_PASSWORD_VALIDATORS=[{
        'NAME':
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator',
    }, {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    }])
    def test_set_password_validation(self):
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))

        # Missing password
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
            })
        self.assertRC(response, 422)
        self.assertJE(
            response, "password.@0", "Empty password is not allowed")

        # Empty string password
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': ''
            })
        self.assertRC(response, 422)
        self.assertJE(
            response, "password.@0", "Empty password is not allowed")

        # None password
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': None
            })
        self.assertRC(response, 422)
        self.assertJE(
            response, "password.@0", "Empty password is not allowed")

        # Invalid password according to UserAttributeSimilarityValidator and
        # MinimumLengthValidator
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'jrr'
            })
        self.assertRC(response, 422)
        self.assertJE(response, 'password.@0',
                      "The password is too similar to the username.")
        self.assertJE(response, 'password.@1',
                      "This password is too short. "
                      "It must contain at least 8 characters.")

        # Finally, a valid password
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': '9ashff8za-@#asd'
            })
        self.assertRC(response, 200)

    def test_set_password_autologin_jwt(self):
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'NEW PASSWORD',
                'autologin': 'jwt'
            })
        self.assertRC(response, 200)
        self.assertIn('token', response.json_content)
        token = response.json_content['token']
        decoded = jwt.decode(
            token, settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)

    def test_set_password_autologin_cookies(self):
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'NEW PASSWORD',
                'autologin': 'cookie'
            })

        self.assertRC(response, 200)
        cookie = [v for k, v in response.client.cookies.items()
                  if k == 'token'][0]
        regex = r".*token=([\w\._-]*);.*"
        token = re.findall(regex, str(cookie))[0]

        self.assertRC(response, 200)
        decoded = jwt.decode(
            token, settings.PFX_SECRET_KEY,
            algorithms="HS256")
        self.assertEqual(decoded['pfx_user_pk'], self.user1.pk)

    def test_set_password_autologin_wrong_value(self):
        token = default_token_generator.make_token(self.user1)
        uid = urlsafe_base64_encode(force_bytes(self.user1.pk))
        response = self.client.post(
            '/api/auth/set-password', {
                'token': token,
                'uidb64': uid,
                'password': 'NEW PASSWORD',
                'autologin': 'qwertz'
            })
        self.assertRC(response, 200)
        self.assertJE(response, 'message', "password updated successfully")

    def test_token_anonymous(self):
        self.client.logout()
        response = self.client.get(
            '/api/books')
        self.assertRC(response, 200)

    @modify_settings(
        MIDDLEWARE={
            'remove': [
                'pfx.pfxcore.middleware.AuthenticationMiddleware']})
    def test_cookie_anonymous(self):
        self.cookie_client.logout()
        response = self.cookie_client.get(
            '/api/books')
        self.assertRC(response, 200)
