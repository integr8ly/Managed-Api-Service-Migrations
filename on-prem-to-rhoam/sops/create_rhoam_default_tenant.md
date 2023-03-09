# Create RHOAM default tenant
This sop covers creation of RHOAMs default tenant in case it doesn't exists in customer database

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
- Impersonate as the tenant and double check that SSO-Integrations can be created
- Go to access tokens and create full access access_token
- Copy the access token and update the system-seed admin token (do not confuse this with master token)