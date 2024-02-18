# srvCloud-keycloak Library #

## What is this? ##
The module allows you to work with keycloak

### Using ###


Using the library is as simple and convenient as possible:

Let's import it first:
First, import everything from the library (use the `from keycloak_srvcloud import Keycloak` construct).

Examples of all operations:

Init class:

    keycloak = Keycloack(keycloak_host, keycloak_port, realm_name, client_id, client_secret)


Init session:

    cookies = keycloak.auth('user', 'password')

Refresh token:

    cookies = keycloak.refresh_token(cookies['access_token'], cookies['refresh_token'])

Close session:

    keycloak.logout(cookies['access_token'], cookies['refresh_token'])

Get introspect:

    introspect = keycloak.introspect(cookies['access_token'])

## Developer ##
Viktor Podlevski

My site: [github](https://github.com/VITca64rus) 