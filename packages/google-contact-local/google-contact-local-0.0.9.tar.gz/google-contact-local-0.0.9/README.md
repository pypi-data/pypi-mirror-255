# google-contact-local-python-package

## Enable People API
https://support.google.com/googleapi/answer/6158841?hl=en<br>

## How to run google-contact-local
### Authentication
First you have to perform the autherntication proccess
google_contacts = GoogleContacts()
google_contacts.authenticate()
It will open an authoentication windows on Google chrome, you'll have to loging
with your Google user
Add the user email as a test user 

### Pull contacts from Google Contacts
Run google_contacts.pull_contacts_with_stored_token("example@example.com")
This will pull the contacts details from your Google Contacts
and store them in the database in https://console.cloud.google on the app OAuth consent screen

## Google People API documentation
https://developers.google.com/people/api/rest<br>

To create local package and remote package layers (not to create GraphQL and REST-API layers)

# Google Contacts
Register in `https://developers.google.com/people/v1/getting-started`<br>

In the credentials section in google cloud application, create a new Create OAuth client ID credential of type "Web application".
The Authorised redirect URIs must have an URL exactly identical to the GOOGLE_REDIRECT_URIS environment variable and if it has a port number it must also be passed to the method "run_local_server"
