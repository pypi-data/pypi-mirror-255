# Standard libraries
import os
import json
import http
import time
import pycountry

# Libraries for Google API and authentication
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account  # noqa: F401
import google.auth  # noqa: F401

# Local imports
from dotenv import load_dotenv
from location_local.locations_local_crud import LocationLocalConstants
from user_external_local.user_externals_local import UserExternalsLocal
from logger_local.LoggerLocal import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from user_context_remote.user_context import UserContext
from contact_local.contact_local import ContactsLocal
from database_mysql_local.generic_crud import GenericCRUD
from contact_group_local.contact_group import ContactGroup
from contact_notes_local.contact_notes_local import ContactNotesLocal
from importer_local.ImportersLocal import ImportersLocal
from contact_phones_local.contact_phones_local import ContactPhonesLocal
from contact_profiles_local.contact_profiles_local import ContactProfilesLocal
from contact_user_externals_local.contact_user_externals_local import ContactUserExternalsLocal
from contact_locations_local.contact_locations_local import ContactLocationsLocal
from internet_domain_local.internet_domain_local import DomainLocal
from location_local.point import Point
from location_local.location_local_constants import LocationLocalConstants
from entity_type.EntityType import EntityType
from contact_persons_local.contact_persons_local import ContactPersonsLocal
from contact_email_address_local.contact_email_addresses_local import ContactEmailAdressesLocal
from api_management_local.indirect import InDirect
from api_management_local.api_limit_status import APILimitStatus
from api_management_local.API_Mangement_Manager import APIMangementManager
from api_management_local.Exception_API import (ApiTypeDisabledException,
                                                ApiTypeIsNotExistException)
from url_remote import action_name_enum, component_name_enum, entity_name_enum
from url_remote.url_circlez import OurUrl
from python_sdk_remote.validate_environment import validate_enviroment_variables
# TODO: add python_sdk_remote.validate to import and call validate environment variables
load_dotenv()

# Static token details
SCOPES = ["https://www.googleapis.com/auth/userinfo.email",
          "https://www.googleapis.com/auth/contacts.readonly",
          "openid"]  # both scopes must be allowed within the project!
# What other scopes can we use?

# Logger setup
GOOGLE_CONTACT_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 188
GOOGLE_CONTACT_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'google-contact-local-python-package/google-contacts.py'
DEVELOPER_EMAIL = 'valeria.e@circ.zone'
obj = {
  'component_id': GOOGLE_CONTACT_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
  'component_name': GOOGLE_CONTACT_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
  'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
  'developer_email': 'valeria.e@circ.zone'
}
logger = Logger.create_logger(object=obj)

BRAND_NAME = os.getenv('BRAND_NAME')
PRODUCT_USER_IDENTIFIER = os.getenv("PRODUCT_USER_IDENTIFIER")
PRODUCT_PASSWORD = os.getenv("PRODUCT_PASSWORD")
AUTHENTICATION_API_VERSION = 1

# TODO: delete the following line when importer.insert()'s parameter location_id will have a default value
DEFAULT_LOCATION_ID = LocationLocalConstants.UNKNOWN_LOCATION_ID


class GoogleContacts(GenericCRUD):
    # Specific id for people api with google contacts
    GOOGLE_CONTACT_SYSTEM_ID = 6
    PEOPLE_API_ID = 16
    DATA_SOURCE_ID = 10

    def __init__(self, is_test_data: bool):
        validate_enviroment_variables()
        self.user_context = UserContext.login_using_user_identification_and_password()
        # TODO: change email1, email2, email3 to email_address1, email_address2, email_address3 in ContactsLocal
        self.contacts_local = ContactsLocal(is_test_data=is_test_data)
        self.profile_id = self.user_context.get_effective_profile_id()
        self.creds = None
        self.email = None
        self.is_test_data = is_test_data
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

        # TODO Can we call a generic function in python-sdk to bring us the value and present error if there is no value. 
        self.port = int(os.getenv("PORT_FOR_AUTHENTICATION"))
        # Change those to consts
        self.redirect_uris = os.getenv("GOOGLE_REDIRECT_URIS")
        self.auth_uri = os.getenv("GOOGLE_AUTH_URI")
        self.token_uri = os.getenv("GOOGLE_TOKEN_URI")
        # TODO: fix https://github.com/circles-zone/entity-type-local-python-package
        # self.contact_entity_type_id = EntityType.get_entity_type_id_by_name("Contact")
        self.contact_entity_type_id = GenericCRUD(default_schema_name="entity_type").select_one_dict_by_id(
            view_table_name="entity_type_ml_en_view",
            select_clause_value="entity_type_id",
            id_column_name="entity_type_name",
            id_column_value="Contact"
        )["entity_type_id"]

        super().__init__(
            default_schema_name="user_external",
            default_table_name="user_external_table",
            default_view_table_name="user_external_view",
            default_id_column_name="user_external_id",
            is_test_data=is_test_data
        )

    def authenticate(self):  # note, missing check for token/email if user already authenticated.
        # usure how to check at the moment.

        logger.start("Getting user authentication")

        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                client_config = {
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": self.redirect_uris,
                        "auth_uri": self.auth_uri,
                        "token_uri": self.token_uri,
                    }
                }
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                # old: self.creds = flow.run_local_server(port=0)
                # if GOOGLE_REDIRECT_URIS is localhost it must be
                # GOOGLE_REDIRECT_URIS=http://localhost:54415/
                # if the port number is 54415 and we must also pass that port
                # to the run_local_server function
                # and also add EXACTLY http://localhost:54415/
                # to Authorised redirect URIs in the 
                # OAuth 2.0 Client IDs in Google Cloud Platform
                self.creds = flow.run_local_server(port=self.port)

            # Fetch the user's email for profile_id in our DB
            service = build('oauth2', 'v2', credentials=self.creds)
            user_info = service.userinfo().get().execute()
            self.email = user_info.get("email")
            # TODO: What else can we get from user_info?

            # Deserialize the token_data into a Python dictionary
            token_data_dict = json.loads(self.creds.to_json())
            # TODO: What other data we can get from token_data_dict?

            # Extract the access_token, expires_in, and refresh_token to insert into our DB
            access_token = token_data_dict.get("token", None)
            expires_in = token_data_dict.get("expiry", None)
            refresh_token = token_data_dict.get("refresh_token", None)

            if access_token:
                UserExternalsLocal.insert_or_update_user_external_access_token(
                    self.email,
                    self.profile_id,
                    self.GOOGLE_CONTACT_SYSTEM_ID,
                    access_token,
                    expires_in,
                    refresh_token
                )
            else:
                logger.error("Access token not found in token_data.")
                # TODO: Shall we raise exception?

        logger.end("Authentication request finished")

    @staticmethod
    def create_dict_representation(contact):
        # Extract the details from the contact
        names = contact.get('names', [{}])[0]
        first_name = names.get('givenName')
        last_name = names.get('familyName')
        display_name = names.get('displayName', None)
        display_name = display_name if display_name else f"{first_name} {last_name}"
        phone_numbers = contact.get('phoneNumbers', [{}])
        '''
        phone_dict structure:
        {
            'value': '054-123-4567',
            'canonicalForm': '+972541234567',
            'type': 'work',
            'formattedType': 'Work'
        }
        '''
        phone_dict1 = phone_numbers[0] if len(phone_numbers) > 0 else None
        phone_dict2 = phone_numbers[1] if len(phone_numbers) > 1 else None
        phone_dict3 = phone_numbers[2] if len(phone_numbers) > 2 else None
        phone_numbers = [phone.get('canonicalForm') for phone in contact.get('phoneNumbers', [{}])]
        emails = [email.get('value') for email in contact.get('emailAddresses', [{}])]
        birthday = contact.get('birthdays', [{}])[0].get('text')
        location_dict = contact.get('addresses', [{}])[0]
        organizations = contact.get('organizations', [{}])[0]
        job_title = organizations.get('title')
        organization = organizations.get('name')
        websites = contact.get('urls', [{}])
        notes = contact.get('biographies')[0].get('value') if contact.get('biographies') else None

        # TODO: change email1, email2, email3 to email_address1, email_address2, email_address3
        # Create the dictionary
        google_contact_dict = {
            "first_name": first_name,
            "last_name": last_name,
            "display_as": display_name,
            "phone_dict1": phone_dict1,
            "phone_dict2": phone_dict2,
            "phone_dict3": phone_dict3,
            "birthday": birthday,
            "location": location_dict,
            "job_title": job_title,
            "organization": organization,
            "notes": notes
        }

        # Add additional phones and emails to the dictionary
        for i in range(0, max(len(phone_numbers), len(emails), len(websites))):
            if i < len(phone_numbers):
                google_contact_dict[f"phone{i + 1}"] = phone_numbers[i]
            if i < len(emails):
                google_contact_dict[f"email{i + 1}"] = emails[i]
            if i < len(websites):
                google_contact_dict[f"website{i + 1}"] = websites[i].get('value')
                google_contact_dict[f"website_type{i + 1}"] = websites[i].get('type')
                google_contact_dict[f"website_formatted_type{i + 1}"] = websites[i].get('formattedType')

        return google_contact_dict

    def pull_people_api(self, email: str):
        logger.start("Pulling Details")
        contact_id = None
        location_id = DEFAULT_LOCATION_ID
        try:
            service = build('people', 'v1', credentials=self.creds)
            # TODO: Shall we use v2? https://gist.github.com/avaidyam/acd66c26bc68bf6b89e70374bdc5a5d4
            logger.info('Listing all connection names along with their emails and phone numbers')

            # Start with an empty token
            page_token = None

            # TODO: before_call_api and after_call_api are supposed to get the argument external_user_id, 
            # but when they get it they fails because the relevant row in  api_limit_view has None 
            # in the column external_user_id. Shall we delete the following lines?
            user_external_id_dict = self.select_one_dict_by_id(select_clause_value="user_external_id",
                                                               id_column_name="username",
                                                               id_column_value=email, order_by="user_external_id DESC")
            user_external_id = user_external_id_dict["user_external_id"]

            authentication_auth_login_endpoint_url = OurUrl.endpoint_url(
                brand_name=BRAND_NAME,
                environment_name=os.getenv('ENVIRONMENT_NAME'),
                component_name=component_name_enum.ComponentName.AUTHENTICATION.value,
                entity_name=entity_name_enum.EntityName.AUTH_LOGIN.value,
                version=AUTHENTICATION_API_VERSION,
                action_name=action_name_enum.ActionName.LOGIN.value
            )
            headers = {"Content-Type": "application/json"}
            outgoing_body = (PRODUCT_USER_IDENTIFIER, PRODUCT_PASSWORD)
            incoming_message = ""
            response_body = ""

            while True:
                try:
                    indirct = InDirect()
                    api_check, api_call_id, arr = indirct.before_call_api(external_user_id=None,
                                                                          api_type_id=self.PEOPLE_API_ID,
                                                                          endpoint=authentication_auth_login_endpoint_url,
                                                                          outgoing_header=headers,
                                                                          outgoing_body=outgoing_body
                                                                          )
                    if arr is None:
                        used_cache = False
                        if api_check == APILimitStatus.BETWEEN_SOFT_LIMIT_AND_HARD_LIMIT:
                            logger.warn("You excced the soft limit")
                        if api_check != APILimitStatus.GREATER_THAN_HARD_LIMIT:
                            try:
                                # user = user_context.login_using_user_identification_and_password(outgoing_body)
                                http_status_code = http.HTTPStatus.OK.value
                            except Exception as exception:
                                logger.exception(object=exception)
                                http_status_code = http.HTTPStatus.BAD_REQUEST.value
                        else:
                            logger.info(" You passed the hard limit")
                            x = APIMangementManager.seconds_to_sleep_after_passing_the_hard_limit(
                                api_type_id=self.PEOPLE_API_ID)
                            if x > 0:
                                logger.info("sleeping : " + str(x) + " seconds")
                                time.sleep(x)
                                # raise PassedTheHardLimitException

                            else:
                                logger.info("No sleeping needed : x= " + str(x) + " seconds")
                    else:
                        used_cache = True
                        logger.info("result from cache")
                        # print(arr)
                        http_status_code = http.HTTPStatus.OK.value

                    results = service.people().connections().list(
                        resourceName='people/me',
                        pageSize=2000,  # Scrolls further in the GoogleContacts sheet, otherwise stops at around 10 contacts.
                        pageToken=page_token,
                        personFields=(
                            'names,emailAddresses,biographies,phoneNumbers,birthdays,addresses,organizations,'
                            'occupations,urls'
                        )
                        ).execute()

                    indirct.after_call_api(external_user_id=None,
                                           api_type_id=self.PEOPLE_API_ID,
                                           endpoint=authentication_auth_login_endpoint_url, outgoing_header=headers,
                                           outgoing_body=outgoing_body,
                                           incoming_message=incoming_message,
                                           http_status_code=http_status_code,
                                           response_body=response_body, api_call_id=api_call_id, used_cache=used_cache)

                    google_connections = results.get('connections', [])

                    for google_contact_connection in google_connections:
                        logger.info(log_message=f"Type of contact: {type(google_contact_connection)}")
                        logger.info(log_message=f"Contents of contact: {google_contact_connection}")

                        # TODO: move these calls to ComprehensiveContacts
                        # Create dictionary representation for the contact
                        contact_dict = GoogleContacts.create_dict_representation(google_contact_connection)

                        # Insert or update the contact in the local database
                        contact_id = self.contacts_local.insert_update_contact(contact_dict)
                        try:
                            # insert link contact_locations
                            location_id = self._insert_link_contact_locations(contact_dict=contact_dict, contact_id=contact_id)
                            if not location_id:
                                location_id = DEFAULT_LOCATION_ID

                            # insert link contact_group
                            self._insert_link_contact_groups(contact_dict=contact_dict, contact_id=contact_id)

                            # insert link contact_persons
                            self._insert_link_contact_persons(contact_dict=contact_dict, contact_id=contact_id)

                            # insert link contact_email_addresses
                            self._insert_link_contact_email_addresses(contact_dict=contact_dict, contact_id=contact_id)

                            # insert link contact_notes
                            self._insert_link_contact_notes_and_text_blocks(contact_dict=contact_dict, contact_id=contact_id)

                            # insert link contact_phones
                            self._insert_link_contact_phones(contact_dict=contact_dict, contact_id=contact_id)

                            # inset link contact_user_externals
                            self._insert_link_contact_user_externals(contact_dict=contact_dict, contact_id=contact_id)

                            # insert link contact_profiles
                            self._insert_contact_profiles(contact_dict=contact_dict, contact_id=contact_id)

                            # insert link contact_internet_domains
                            self._insert_link_contact_domains(contact_dict=contact_dict, contact_id=contact_id)

                        except Exception as exception:
                            logger.exception(log_message="Error while inserting to contact connection tables",
                                             object={"exception": exception})
                            raise exception
                        finally:
                            importer_id = self._insert_importer(contact_id=contact_id, location_id=location_id,
                                                                user_external_id=user_external_id)



                    # TODO: Add contact_person directly or using ContactPersonsLocal.insert() from GenericCRUD

                    # Break after processing one contact - for debugging without running over all contacts heh
                    # break

                    page_token = results.get('nextPageToken')
                    if not page_token:
                        break
                except ApiTypeDisabledException:
                    logger.error("Api Type Disabled Exception")
                except ApiTypeIsNotExistException:
                    logger.error("Api Type Is Not Exist Exception")
            logger.end("Finished Pulling Details")

        except HttpError as err:
            logger.exception("Error while retrieving contacts from Google using People API and inserting the contact", err)
            logger.end()


    # def _display_contact_details(self, contact):  # for debugging, can delete later
    #     def display_with_names(header, values):
    #         if not values:
    #             print(f"{header}: None")
    #             return
    #         for value in values:
    #             first_name = contact['names'][0].get('givenName', None) if 'names' in contact else None
    #             last_name = contact['names'][0].get('familyName', None) if 'names' in contact else None
    #             print(f"{header} for {first_name} {last_name}: {value}")

    #     # Display names
    #     if 'names' in contact:
    #         names = contact['names']
    #         if names:
    #             first_name = names[0].get('givenName', None)
    #             last_name = names[0].get('familyName', None)
    #             print(f"Name: {first_name} {last_name}")
    #         else:
    #             print("Name: None")
    #     else:
    #         print("Name: None")

    #     # Display emails
    #     emails = [email.get('value', None) for email in contact.get('emailAddresses', [])]
    #     display_with_names("Email", emails)

    #     # Display phone numbers
    #     phone_numbers = [phone.get('value', None) for phone in contact.get('phoneNumbers', [])]
    #     display_with_names("Phone Number", phone_numbers)

    #     # Display birthdays
    #     birthdays = [birthday.get('text', None) for birthday in contact.get('birthdays', [])]
    #     display_with_names("Birthday", birthdays)

    #     # Display addresses
    #     addresses = [address.get('formattedValue', None) for address in contact.get('addresses', [])]
    #     display_with_names("Address", addresses)

    #     # Display organizations
    #     organizations = [org.get('name', None) for org in contact.get('organizations', [])]
    #     display_with_names("Organization", organizations)

    #     # Display occupations
    #     occupations = [occ.get('value', None) for occ in contact.get('occupations', [])]
    #     display_with_names("Occupation", occupations)


    def pull_contacts_with_stored_token(self, email):
        logger.start("Pulling Details From Existing User", object={"email": email})
        if not email:
            logger.error("Email cannot be null.")
            return

        logger.info("Getting token data from DB", object={"email": email, "profile_id": self.profile_id})
        token_data = UserExternalsLocal.get_auth_details(email, self.GOOGLE_CONTACT_SYSTEM_ID, self.profile_id)

        # Unpack the token_data tuple into its constituent parts
        access_token, refresh_token, expiry = token_data

        # Update the token_info dictionary with the unpacked values
        token_info = {
            'token': access_token,
            'refresh_token': refresh_token,
            'token_uri': self.token_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scopes': SCOPES,
            'expiry': expiry  # Already in string format, no need to convert
        }

        # Create a Credentials object from the stored token
        try:
            self.creds = Credentials.from_authorized_user_info(token_info)

            # Print all attributes of self.creds for debugging
            for attr in dir(self.creds):
                if not attr.startswith("__"):
                    print(f"{attr}: {getattr(self.creds, attr)}")

            if not self.creds.valid:
                logger.error("Stored credentials are not valid.")
                logger.error(f"Token info: {token_info}")
                return
        except Exception as e:
            logger.error(f"Exception while creating credentials: {e}")
            logger.end()
            return

        # Now, pull the contacts using the People API
        self.pull_people_api(email)
        logger.end("Finished Pulling From Existing User")

    def _insert_link_contact_groups(self, contact_dict: dict, contact_id: int) -> list:
        logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id})
        groups = []
        groups_linked = None
        if contact_dict.get("organization"):
            groups.append(contact_dict.get("organization"))
        if contact_dict.get("job_title"):
            groups.append(contact_dict.get("job_title"))
        if len(groups) > 0:
            contact_group = ContactGroup()
            groups_linked = contact_group.insert_contact_and_link_to_existing_or_new_group(
                contact_dict=contact_dict,
                contact_id=contact_id,
                groups=groups,
                is_test_data=self.is_test_data)
        logger.end(object={"groups_linked": groups_linked})
        return groups_linked

    def _insert_link_contact_persons(self, contact_dict: dict, contact_id: int) -> int:
        logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id})
        contact_persons = ContactPersonsLocal()
        contact_person_id = contact_persons.insert_contact_and_link_to_existing_or_new_person(
            contact_dict=contact_dict,
            contact_email_address=contact_dict["email1"],
            contact_id=contact_id
        )
        logger.end(object={"contact_person_id": contact_person_id})
        return contact_person_id

    def _insert_link_contact_email_addresses(self, contact_dict, contact_id):
        logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id})
        email1 = contact_dict.get("email1")
        email2 = contact_dict.get("email2")
        email3 = contact_dict.get("email3")
        contact_email_addresses = ContactEmailAdressesLocal()
        if email1:
            contact_email_addresses.insert_contact_and_link_to_email_address(
                contact_dict=contact_dict,
                contact_email_address=email1,
                contact_id=contact_id
            )
        if email2:
            contact_email_addresses.insert_contact_and_link_to_email_address(
                contact_dict=contact_dict,
                contact_email_address=email2,
                contact_id=contact_id
            )
        if email3:
            contact_email_addresses.insert_contact_and_link_to_email_address(
                contact_dict=contact_dict,
                contact_email_address=email3,
                contact_id=contact_id
            )
        logger.end()

    def _insert_link_contact_notes_and_text_blocks(self, contact_dict: dict, contact_id: int) -> int:
        try:
            logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id})
            contact_notes = ContactNotesLocal(
                contact_dict=contact_dict,
                contact_id=contact_id,
                profile_id=self.profile_id
            )
            contact_note_id = contact_notes.insert_contact_notes()
            contact_notes.insert_contact_note_text_block_table(contact_note_id=contact_note_id)
            logger.end(object={"contact_note_id": contact_note_id})
            return contact_note_id
        except Exception as exception:
            logger.exception(log_message="Error while inserting to contact_notes and text_blocks",
                             object={"exception": exception})
            return None

    def _insert_link_contact_phones(self, contact_dict: dict, contact_id: int):
        logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id})
        phone_dict1 = contact_dict.get("phone_dict1")
        phone1 = phone_dict1.get("canonicalForm") if phone_dict1 else None
        phone_dict2 = contact_dict.get("phone_dict2")
        phone2 = phone_dict2.get("canonicalForm") if phone_dict2 else None
        phone_dict3 = contact_dict.get("phone_dict3")
        phone3 = phone_dict3.get("canonicalForm") if phone_dict3 else None
        contact_phones = ContactPhonesLocal()
        if phone1:
            contact_phones.insert_contact_and_link_to_existing_or_new_phone(
                contact_dict=contact_dict,
                phone_number=phone1,
                contact_id=contact_id
            )
        if phone2:
            contact_phones.insert_contact_and_link_to_existing_or_new_phone(
                contact_dict=contact_dict,
                phone_number=phone2,
                contact_id=contact_id
            )
        if phone3:
            contact_phones.insert_contact_and_link_to_existing_or_new_phone(
                contact_dict=contact_dict,
                phone_number=phone3,
                contact_id=contact_id
            )
        logger.end()

    def _insert_link_contact_user_externals(self, contact_dict: dict, contact_id: int) -> int:
        logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id})
        contact_user_externals = ContactUserExternalsLocal()
        contact_user_external_id = contact_user_externals.insert_contact_and_link_to_existing_or_new_user_external(
            contact_dict=contact_dict,
            contact_email_address=contact_dict["email1"],
            contact_id=contact_id,
            user_external_dict={"username": contact_dict["email1"]}
        )
        logger.end(object={"contact_user_external_id": contact_user_external_id})
        return contact_user_external_id

    def _insert_contact_profiles(self, contact_dict: dict, contact_id: int) -> int:
        logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id})
        contact_profiles = ContactProfilesLocal()
        contact_profile_id = contact_profiles.insert_and_link_contact_profile(
            contact_dict=contact_dict,
            contact_id=contact_id
        )
        logger.end(object={"contact_profile_id": contact_profile_id})
        return contact_profile_id

    def _insert_link_contact_domains(self, contact_dict: dict, contact_id: int) -> list[dict]:
        logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id})
        website_count = 1
        website_url = contact_dict.get("website" + str(website_count))
        domain_insert_information_list = []
        while website_url:
            domain = DomainLocal()
            domain_insert_information = domain.link_contact_to_domain(contact_id=contact_id,  # noqa: F841
                                                                      url=website_url)
            domain_insert_information_list.append(domain_insert_information)
            website_count += 1
            website_url = contact_dict.get("website" + str(website_count))
        logger.end(object={"domain_insert_information_list": domain_insert_information_list})
        return domain_insert_information_list

    def _insert_link_contact_locations(self, contact_dict: dict, contact_id: int) -> int:
        logger.start(object={"contact_dict": contact_dict, "contact_id": contact_id})
        contact_locations = ContactLocationsLocal()
        location_dict = self._procces_location_of_google_contact(location_dict=contact_dict["location"])
        contact_location_id = contact_locations.insert_contact_and_link_to_location(
            contact_dict=contact_dict,
            location_dict=location_dict,
            contact_id=contact_id
        )
        location_id_dict = contact_locations.select_one_dict_by_id(
            select_clause_value="location_id",
            id_column_name="contact_location_id",
            id_column_value=contact_location_id
        )
        location_id = location_id_dict.get("location_id")
        logger.end(object={"contact_location_id": contact_location_id, "location_id": location_id})
        return location_id

    def _insert_importer(self, contact_id: int, location_id: int, user_external_id: int) -> int:
        logger.start(object={"contact_id": contact_id, "location_id": location_id, "user_external_id": user_external_id})
        importer = ImportersLocal()
        importer_id = importer.insert(
            data_source_id=self.DATA_SOURCE_ID, location_id=location_id,
            entity_type_id=self.contact_entity_type_id,
            entity_id=contact_id, url="www.google.com",
            user_external_id=user_external_id
        )
        importer.connection.commit()
        logger.end(object={"importer_id": importer_id})
        return importer_id

    # TODO: see if you can improve this method
    def _procces_location_of_google_contact(self, location_dict: dict) -> dict:
        """
        Process location of google contact
        :param location_dict: location_dict
        :return: location_dict
        """
        logger.start(object={"location_dict": location_dict})
        if not location_dict:
            logger.end(log_message="location_dict is None")
            return None
        # TODO: How can we add location type?
        country_code = location_dict.get('countryCode')
        country = pycountry.countries.get(alpha_2=country_code)
        country_name = country.name.upper() if country else None
        location_dict = {
            "address_local_language": location_dict.get('streetAddress'),
            "city": location_dict.get('city'),
            "postal_code": location_dict.get('postalCode'),
            "country": country_name,
            "coordinate": Point(0, 0),
            "neighborhood": LocationLocalConstants.DEFAULT_NEGIHBORHOOD_NAME,
            "county": LocationLocalConstants.DEFAULT_COUNTY_NAME,
            "state": LocationLocalConstants.DEFAULT_STATE_NAME,
            "region": LocationLocalConstants.DEFAULT_REGION_NAME,

        }
        logger.end(object={"location_dict": location_dict})
        return location_dict


if __name__ == '__main__':
    fetcher = GoogleContacts()
    fetcher.authenticate()
    fetcher.pull_people_api()
    fetcher.pull_contacts_with_stored_token("valerka.prov@gmail.com")  # "example@example.com"
