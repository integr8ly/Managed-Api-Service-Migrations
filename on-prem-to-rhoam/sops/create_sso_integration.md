# Create SSO integration with additional tenants

This SOP covers a scenario when SSO integration must be created for additional (non default RHOAMs 3scale tenant) on cluster

## Pre-req
- access to 3scale master portal (this is due to the fact that each tenant where SSO integration must be created must be accessed via impersonation)
- access to RHSSO instance running on cluster

## Envs
```
RHSSO_NAMESPACE=redhat-rhoam-rhsso
```
```
TENANT_NAME=<org name of the tenant>
```
```
WILDCARD_DOMAIN=$(oc get routes console -n openshift-console -o json | jq -r '.status.ingress[0].routerCanonicalHostname' | sed 's/router-default.//')
```
## Create keycloak client

Each new SSO integration requires its own keycloak client created

```
oc apply -f - -n $RHSSO_NAMESPACE <<EOF
apiVersion: keycloak.org/v1alpha1
kind: KeycloakClient
metadata:
  name: $TENANT_NAME
spec:
  client:
    enabled: true
    clientAuthenticatorType: client-secret
    fullScopeAllowed: true
    redirectUris:
      - 'https://$TENANT_NAME-admin.$WILDCARD_DOMAIN/*'
    access:
      configure: true
      manage: true
      view: true
    clientId: $TENANT_NAME
    rootUrl: 'https://$TENANT_NAME-admin.$WILDCARD_DOMAIN'
    implicitFlowEnabled: false
    publicClient: false
    standardFlowEnabled: true
    protocolMappers:
      - config:
          access.token.claim: 'true'
          claim.name: given_name
          id.token.claim: 'true'
          jsonType.label: String
          user.attribute: firstName
          userinfo.token.claim: 'true'
        consentRequired: true
        consentText: '${givenName}'
        name: given name
        protocol: openid-connect
        protocolMapper: oidc-usermodel-property-mapper
      - config:
          access.token.claim: 'true'
          claim.name: email_verified
          id.token.claim: 'true'
          jsonType.label: String
          user.attribute: emailVerified
          userinfo.token.claim: 'true'
        consentRequired: true
        consentText: '${emailVerified}'
        name: email verified
        protocol: openid-connect
        protocolMapper: oidc-usermodel-property-mapper
      - config:
          access.token.claim: 'true'
          id.token.claim: 'true'
        consentRequired: true
        consentText: '${fullName}'
        name: full name
        protocol: openid-connect
        protocolMapper: oidc-full-name-mapper
      - config:
          access.token.claim: 'true'
          claim.name: family_name
          id.token.claim: 'true'
          jsonType.label: String
          user.attribute: lastName
          userinfo.token.claim: 'true'
        consentRequired: true
        consentText: '${familyName}'
        name: family name
        protocol: openid-connect
        protocolMapper: oidc-usermodel-property-mapper
      - config:
          attribute.name: Role
          attribute.nameformat: Basic
          single: 'false'
        consentText: '${familyName}'
        name: role list
        protocol: saml
        protocolMapper: saml-role-list-mapper
      - config:
          access.token.claim: 'true'
          claim.name: email
          id.token.claim: 'true'
          jsonType.label: String
          user.attribute: email
          userinfo.token.claim: 'true'
        consentRequired: true
        consentText: '${email}'
        name: email
        protocol: openid-connect
        protocolMapper: oidc-usermodel-property-mapper
      - config:
          access.token.claim: 'true'
          claim.name: org_name
          id.token.claim: 'true'
          jsonType.label: String
          user.attribute: org_name
          userinfo.token.claim: 'true'
        consentText: n.a.
        name: org_name
        protocol: openid-connect
        protocolMapper: oidc-usermodel-property-mapper
    directAccessGrantsEnabled: false
  realmSelector:
    matchLabels:
      sso: integreatly
EOF
```

## Integrate with the new client

Pull the secret from the secret created by RHSSO:
```
secret=$(oc get secrets/keycloak-client-secret-$TENANT_NAME -n $RHSSO_NAMESPACE -o template --template={{.data.CLIENT_SECRET}} | base64 -d -w 0)
echo "The client id is: $TENANT_NAME and the client secret is: $secret"
```

- Navigate to 3scale master portal
- Select tenant that you wish to create integration for
- Go to accounts settings
- Go to Users > SSO Integrations
- New SSO Integration
```
Provider: Red Hat Single Sign-On
Client: the client ID from previous command
Client Secret: the client secret from previous command
Realm or Site: https://<keycloak edge route from rhsso routes>/auth/realms/openshift - for example: https://keycloak-edge-redhat-rhoam-rhsso.apps.mstoklus-ccs.mjhc.s1.devshift.org/auth/realms/openshift
```