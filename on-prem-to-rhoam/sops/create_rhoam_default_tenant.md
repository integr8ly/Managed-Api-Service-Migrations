# Create RHOAM default tenant
This sop covers creation of RHOAMs default tenant in case it doesn't exist in the customer database

## Log in to 3scale Master Portal

- Navigate to redhat-rhoam-3scale > routes.
- Find master route and access it
- Navigate to system-seed secret under redhat-rhoam-3scale namespace
- Copy the master password
- Login to 3scale master portal with Username: 'master' and password obtained from the secret in previous step
- Navigate to accounts
- Create tenant
```
username: admin
email: admin@3scale.<wildacard domain> example: "admin@3scale.apps.mstoklus-ccs.mjhc.s1.devshift.org"
password: copy the password from system-seed admin password
org: 3scale
```
- Once created, navigate back to accounts
- Locate the 3scale tenant that just got created and click "Activate"
- Log in as the tenant and double check that SSO-Integrations can be created (please note - do not use impersonation feature as it has limitations)
- Go to access tokens and create a new access token with full privileges (check all Scopes and select Read & Write Permissions)
- Copy the access token and update the system-seed Secret's admin token (do not confuse this with the master token) in **both** the red-rhoam-operator and the redhat-rhoam-3scale namespaces