# Authentication

Django PFX offers services and middlewares for managing user authentication in your API.
These services replicate some of the functionalities provided by the `django.contrib.auth`
package but in the form of RESTful services.
They utilize the same user model and authentication backend features,
including password validation and hashing.

## User Model

You have the option to use the standard `django.contrib.auth.models.User`,
but you may prefer to use your own model. To do this, create your own user class.

```python
from django.contrib.auth.models import AbstractUser

class MyUser(AbstractUser):
    pass
```

Then, define the model in your settings:

```python
AUTH_USER_MODEL = "myapp.MyUser"
```

## Authentication Modes

There are two authentication modes available: cookie and bearer token. You can activate either or both by enabling the following middlewares:

* `'pfx.pfxcore.middleware.AuthenticationMiddleware'` (bearer token)
* `'pfx.pfxcore.middleware.CookieAuthenticationMiddleware'` (cookie)

### Token Validity

You can customize token validity by configuring these parameters:

* `PFX_TOKEN_SHORT_VALIDITY`: Validity for short-validity tokens (optional, default `{'hours': 12}`)
* `PFX_TOKEN_LONG_VALIDITY`: Validity for long-validity tokens (optional, default `{'days': 30}`)

### Cookie Settings

To use the `CookieAuthenticationMiddleware`, you need to configure the following settings:

* `PFX_COOKIE_DOMAIN`: The cookie domain
* `PFX_COOKIE_SECURE`: `Secure` attribute of the cookie (`True`/`False`)
* `PFX_COOKIE_SAMESITE`: `SameSite` attribute of the cookie (`'Strict'`/`'Lax'`/`'None'`)

See the [MDN Website](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies) for more details.

## Services

### Login
A login rest services with a `mode` parameter to choose between JWT bearer token or cookie authentication.
In cookie mode, the JWT token is saved in an HTTP-only cookie.

**Request :** `POST` `/auth/login?mode=<mode>`

**Request body:**

| Field       | Description                         |
|-------------|-------------------------------------|
| username    | the username                        |
| password    | the password                        |
| remember_me | If true, use a long validity token. |

**Responses :**

* `HTTP 401` if the credentials are incorrect
* `HTTP 200` with the following body

| Field | Description                            |
|-------|----------------------------------------|
| token | the jwt token. (only if mode is 'jwt') |
| user  | the user object                        |


### Logout
A service that deletes the authentication cookie if it exists.

**Request :** `GET` `/auth/logout`

**Responses :** `HTTP 200` OK with a success message.


### Change Password
A service to change the password of an authenticated user.

**Request :** `POST` `/auth/change-password`

**Request body :**

| Field        | Description          |
|--------------|----------------------|
| old_password | the current password |
| new_password | the new password     |

**Responses :**
* `HTTP 422` if any validation error
* `HTTP 200` OK with a success message.

### Forgotten Password
A service that allows users to request a password reset. This service sends an email to the user containing
a link to a "set password" page, which your frontend software must implement.

You must set `PFX_RESET_PASSWORD_URL` in your settings to define this "set password" link.
The link must include the `token` and `uidb64` parameters,
like so: `https://example.com/reset-password?token={token}&uidb64={uidb64}`.
Your reset page should then call the "set password" service with these two parameters.

You can override this class if you need to customize the email templates.
Refer to the [API doc](api.views.rst#pfx.pfxcore.views.ForgottenPasswordView) for more details.

**Request :** `POST` `/auth/forgotten-password`

**Request body :**

| Field | Description              |
|-------|--------------------------|
| email | the user's email address |

**Responses :**
* `HTTP 200` OK with a success message.
* `HTTP 422` Error if the email parameter is not an email address

### Sign Up
A service that allows visitors to sign up.
This service sends a welcome email to the user containing a link to a "set password" page,
which your frontend software must implement.

You must set `PFX_RESET_PASSWORD_URL` in your settings to define this "set password" link.
The link should include the `token` and `uidb64` parameters,
like so: `https://example.com/reset-password?token={token}&uidb64={uidb64}`.
Your reset page should then call the "set password" service with these two parameters.

You can override this class if you need to customize the user or email templates.
Refer to the [API doc](api.views.rst#pfx.pfxcore.views.SignupView) for more details.

**Request :** `POST` `/auth/signup`

**Request body :**

| Field      | Description              |
|------------|--------------------------|
| first_name | the user's first name    |
| last_name  | the user's  last name    |
| username   | the user name            |
| email      | the user's email address |

**Responses :**
* `HTTP 422` if there are validation error.
* `HTTP 200` OK with a success message.

### Set Password
A service for setting the password using a UID and a token provided
in the email sent by the "forgotten password" or "sign up" services.

**Request :** `POST` `/auth/set-password`

**Request body :**

| Field     | Description                                                   |
|-----------|---------------------------------------------------------------|
| uidb64    | the uid in base64 sent in the set/reset password link         |
| token     | the reset password token sent in the set/reset password link  |
| password  | the new password                                              |
| autologin | Automatically logs the user in upon successful authentication |

_Autologin value must match the login's `mode` parameters (`cookie` or `jwt`)._

**Responses :**
* `HTTP 401` if the token or uidb64 is invalid
* `HTTP 422` if there are validation error.
* `HTTP 200` OK with a success message.

### Validate User Token
You can use this service to validate the token and `uidb64` before the
"Set Password" service is called, such as when a user opens the "set password"
page of your frontend application.

**Request :** `POST` `/auth/validate-user-token`

**Request body :**

| Field     | Description                                                   |
|-----------|---------------------------------------------------------------|
| uidb64    | the uid in base64 sent in the set/reset password link         |
| token     | the reset password token sent in the set/reset password link  |


**Responses :**
* `HTTP 422` if the data are invalid
* `HTTP 200` OK with a success message.
