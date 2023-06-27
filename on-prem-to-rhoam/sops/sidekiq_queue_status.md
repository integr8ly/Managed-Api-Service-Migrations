# Check the 3scale queues status

To check 3scale queues status:

- Login to the 3scale master portal (the username and password can be found in the `system-seed` Secret)
- Change the URL from <WILDCARD_DOMAIN/p/admin/dashboard> to <WILDCARD_DOMAIN/sidekiq>
- On the menu bar at the top navigate to "Queues" and confirm that the size of the queues is `0`, if not, confirm that it's going down
- In case of retries being present, you can navigate to "Retries" tab and click "Retry Now" to speed up the process of re-trying. 
- In general, the "Busy", "Scheduled" and "Retries" should be empty prior to the migration 

