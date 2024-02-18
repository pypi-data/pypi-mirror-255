####################################################################
#   Copyright (C) 2020-2024 Luis Falcon <falcon@gnuhealth.org>
#   Copyright (C) 2020-2024 GNU Solidario <health@gnusolidario.org>
#   License: GPL v3+
#   Please read the COPYRIGHT and LICENSE files of the package
####################################################################

import bcrypt
import logging
import datetime
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from mygnuhealth.core import maindb, get_personal_key, \
                             check_date, get_user_profile


class UserAccount():
    """This class manages the login and initialization of the personal key

        Properties:
        -----------
            login_success: True when entering the correct personal key
            wrong_date: True when an invalid date is found

            account_exist: True when the user account has been created
            today_date: current date

        Methods:
        --------
            init_personal_key: Sets the personal key at the initial run.
            login: Receives the personal key to login, and checks
                if it is the correct one to log in.
            create_account: Receives the initial personal key to
                create an account.

    """

    def get_date(self):
        """
        Returns the date packed into an array (day,month,year)
        """
        rightnow = datetime.datetime.now()
        dateobj = []
        dateobj.append(rightnow.day)
        dateobj.append(rightnow.month)
        dateobj.append(rightnow.year)
        return dateobj

    def account_exist(self):
        """
        Check if an account exist in the database.
        It basically checks for the "credentials" table, created
        at user initialization.
        """
        if (maindb.table('credentials')):
            print("DB is initialized")
            rc = True

        else:
            print("We need to init the personal Key")
            rc = False

        return rc

    def update_profile(self, profile):
        # Include height and other user settings at initialization
        profiletable = maindb.table('profile')
        if (len(profiletable) > 0):
            print(f"Updating profile ... {profile}")
            profiletable.update(profile)

        else:
            print(f"Initializing profile. Setting profile {profile}")
            profiletable.insert(profile)

    def init_personal_key(self, key):
        encrypted_key = bcrypt.hashpw(key.encode('utf-8'),
                                      bcrypt.gensalt()).decode('utf-8')

        credentials_table = maindb.table('credentials')
        if (len(credentials_table) > 0):
            credentials_table.update({'personal_key': encrypted_key})
        else:
            logging.info("Initializing credentials table")
            credentials_table.insert({'personal_key': encrypted_key})

        logging.info(f"Initialized personal key: {encrypted_key}")
        return encrypted_key

    def get_username(self):
        if get_user_profile(maindb):
            return get_user_profile(maindb)['username']

    def login(self, key):
        key = key.encode()

        personal_key = get_personal_key(maindb)

        if bcrypt.checkpw(key, personal_key):
            logging.info("Login correct - Move to main PHR page")
            return True
        else:
            logging.info("Wrong login credentials")
            return False

    def createAccount(self, key, key_repeat,
                      height, personname, birthdate, sex):
        # Retrieves the information from the initialization form
        # Initializes user profile and sets the initial password
        validation_process = True
        errors = []
        profile = {}

        if (height):
            # Sets the user height
            height = int(height)
            profile['height'] = height

        if (personname):
            # Sets the user name
            profile['username'] = personname
        else:
            errors.append("Name")
            validation_process = False

        if (birthdate):
            if (check_date(birthdate)):
                # Sets the birthdate
                year, month, day = birthdate
                daterp = str(datetime.date(int(year), int(month), int(day)))
                profile['birthdate'] = daterp
            else:
                print("Wrong Date!")
                errors.append("Date")
                validation_process = False
                self.wrong_date = True

        # The label -and default value- is "Sex",
        # so we update only if another value is chosen
        if (sex != "Sex"):
            # Sets the user sex
            profile['sex'] = sex
        else:
            errors.append("Sex")
            validation_process = False

        if (key and (key == key_repeat)):
            key = key.encode()
        else:
            errors.append("Personal Key")
            validation_process = False

        if (validation_process and
                self.init_personal_key(key.decode('utf-8'))):
            self.update_profile(profile)

            self.login_success = True
            # If all the info is OK and move to the login screen
            return True

        else:
            popup = Popup(title='Wrong values',
                          content=Label(text=f"Please check {errors}"),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()
