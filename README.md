## Flask Okta integration template repo

This repo serves as a minimal example of using Flask with Okta, using the same dependencies as Apache SuperSet project. It was made because I was frustrated that none of the guides on using SuperSet with Okta were working. It remains as a nice Proof of concept, and future debugging environment for that software OAuth 2.0 (OIDC) with Okta.

### Requirements / System setup

* [python](https://www.python.org) 3.11+
* set environment variables (you'll need to edit launch.json if you plan on using VSCode built-in debugger)

#### Suggested

* homebrew (OSX)
* Use a virtual environment with `python -m venv .venv`
* Activate virtual environment with `. .venv/bin/activate`

### Python packages

```shell
pip install Flask Flask-AppBuilder Authlib requests
```

### Running

```shell
FLASK_APP=main.py python -m flask run --debug --port 8088
```

### Workaround

This workaround gets Okta working again for my setup 2024-12-07. You patch `.venv/lib/python3.11/site-packages/flask_appbuilder/security/manager.py`

It uses the fact that `.venv/lib/python3.11/site-packages/authlib/integrations/flask_client/apps.py` (helpfully the last few lines) sets the session token to contain the id token and properties from the id token.

```python
        # for Okta
        if provider == "okta":
            data = self.appbuilder.sm.oauth_remotes[provider].userinfo()
            if data is None:
                me = self.appbuilder.sm.oauth_remotes[provider].get("userinfo")
                data = me.json()
```

Prior to this it read

```python
        # for Okta
        if provider == "okta":
            me = self.appbuilder.sm.oauth_remotes[provider].get("userinfo")
            data = me.json()
```

This is supposed to call the `POST <okta-base-url>/oauth2/v1/userinfo` endpoint, but for whatever reason doesn't succeed and gets a HTTP 404.

With Curl I can reach the endpoint just fine, using the access token, likely due to my grants, but the access token I took from the response that was built using a debugger and `self.appbuilder.sm.oauth_remotes[provider]`. In-short I think that I can't recommend the libraries, as they are grossly over-complicated and feel poorly documented and maintained.
