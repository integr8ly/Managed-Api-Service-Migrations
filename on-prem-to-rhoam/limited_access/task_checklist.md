# Tracker for limited access migration

Below is a tracker of the steps performed to help to keep track of "completed" tasks during migration.

# Access confirmation - day / days prior to migration

### Migration environment:

<b> Note. In the event of migration being performend on production cluster, disregard this section </b>

1. - [ ] Access to RHOAM Eng migration cluster

2. Access to RHOAM Eng AWS:
- [ ] account number (not required if not relying on UI)
- [ ] region
- [ ] secret
- [ ] id

3. AWS has resources created:
- [ ] Standalone VPC created
- [ ] MySQL 5.38
- [ ] Postgres 13
- [ ] 2x Redis instances

### Production environment:

1. Access to RHOAM production cluster:
- [ ] oc login commands
- [ ] console
- [ ] RHOAM Installation Paused at the production cluster after APIManager creation

2. Access to production AWS account:
- [ ] region
- [ ] secret
- [ ] id

## Red Hat Pre-requisites
1. - [ ] Pre-requisite 1 completed
2. - [ ] Pre-requisite 2 completed
3. - [ ] Pre-requisite 3 completed
4. - [ ] Pre-requisite 4 completed
5. - [ ] Pre-requisite 5 completed
6. - [ ] Pre-requisite 6 completed

## Customer / Red Hat Pre-requisistes
1. - [ ] Pre-requisite 1 completed
2. - [ ] Pre-requisite 2 completed
3. - [ ] Pre-requisite 3 completed
4. - [ ] Pre-requisite 4 completed
5. - [ ] Pre-requisite 5 completed
6. - [ ] Pre-requisite 6 completed
7. - [ ] Pre-requisite 7 completed
8. - [ ] Pre-requisite 8 completed

# Migration Required files

1. - [ ] system database dump available
2. - [ ] backend redis dump available
3. 3scale secrets available:
- [ ] system-app
- [ ] system-events-hook
- [ ] system-master-apicast
- [ ] system-memcache
- [ ] system-recaptcha
- [ ] system-seed

### Migration cluster:

Pre-req
- [ ] oc logged in to migration cluster
- [ ] logged in to AWS migration account

1. - [ ] Step 3 completed
2. - [ ] Step 4 completed
3. - [ ] Step 5 completed
4. - [ ] Step 6 completed
5. - [ ] Step 7 completed
6. - [ ] Step 8 completed
7. - [ ] Step 9 completed
8. - [ ] Step 10 completed
9. - [ ] Step 11 completed
10. - [ ] Step 12 completed

### Production cluster:

Pre-req:
- [ ] oc logged in to production cluster
- [ ] logged in to AWS production account

1. - [ ] Step 13 completed
2. - [ ] Step 14 completed
3. - [ ] Step 15 completed
4. - [ ] Step 16 completed
5. - [ ] Step 17 completed

### Production cluster config

Pre-req:
- [ ] access to production cluster console 
- [ ] oc logged in to production cluster

1. - [ ] Step 18 completed
2. - [ ] Step 19 completed
3. - [ ] Step 20 completed
4. - [ ] Step 21 completed
5. - [ ] Step 22 completed

### Customer actions required

Pre-req:
- All previous steps completed
- IDP Configured

1. - [ ] Step 23 completed
