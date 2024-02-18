##############################################################################
#
#    MyGNUHealth : Mobile and Desktop PHR node for GNU Health
#
#           MyGNUHealth is part of the GNU Health project
#
##############################################################################
#
#    GNU Health: The Libre Digital Health Ecosystem
#    Copyright (C) 2008-2024 Luis Falcon <falcon@gnuhealth.org>
#    Copyright (C) 2011-2024 GNU Solidario <health@gnusolidario.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import bcrypt
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import get_personal_key, get_user_profile, \
                 get_federation_account, maindb


class ProfileSettings():

    def check_current_password(current_password):
        personal_key = get_personal_key(maindb)
        cpw = current_password.encode()
        rc = bcrypt.checkpw(cpw, personal_key)
        if not rc:
            popup = Popup(title='Wrong password',
                          content=Label(text="Current password"
                                        " does not match"),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

        return rc

    def check_new_password(password, password_repeat):
        rc = None
        print(len(password))
        if ((password == password_repeat) and (len(password) > 2)):
            rc = password
        if not rc:
            popup = Popup(title='Wrong values',
                          content=Label(text="Passwords don't"
                                        " match or key is too small"),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()
        return rc

    def update_personalkey(password):
        encrypted_key = bcrypt.hashpw(password.encode('utf-8'),
                                      bcrypt.gensalt()).decode('utf-8')

        credentialstable = maindb.table('credentials')
        if (len(credentialstable) > 0):
            credentialstable.update({'personal_key': encrypted_key})
        else:
            print("Initializing credentials table")
            credentialstable.insert({'personal_key': encrypted_key})

        print("Saved personal key", encrypted_key)

    def update_profile(profile):
        profiletable = maindb.table('profile')
        if (len(profiletable) > 0):
            print(f"Updating height to {profile['height']}")
            profiletable.update({'height': profile['height']})

        else:
            print(f"Initializing profile. Setting height {profile['height']}")
            profiletable.insert({'height': profile['height']})

        popup = Popup(title='Success!',
                      content=Label(text="Height succesfully"
                                    " updated"),
                      size_hint=(0.5, 0.5), auto_dismiss=True)
        popup.open()

        return True

    def set_height(height):
        profile_height = {'height': height}
        if (height):
            ProfileSettings.update_profile(profile_height)

    def update_fedacct(fedacct):
        fedtable = maindb.table('federation')
        if (len(fedtable) > 0):
            fedtable.update({'federation_account': fedacct})
        else:
            print("Initializing federation settings")
            fedtable.insert({'federation_account': fedacct})

        popup = Popup(title='Success!',
                      content=Label(text="Federation account succesfully"
                                    " updated"),
                      size_hint=(0.5, 0.5), auto_dismiss=True)
        popup.open()

        return True

    def set_fedacct(userfedacct):
        if (userfedacct):
            ProfileSettings.update_fedacct(userfedacct)

    def validate_pkey_update(current_password, password,
                             password_repeat):
        if (ProfileSettings.check_current_password(current_password) and
                ProfileSettings.check_new_password(password, password_repeat)):
            print("Pkey validation OK... updating personal key")
            ProfileSettings.update_personalkey(password)
            popup = Popup(title='Success!',
                          content=Label(text="Personal Key sucessfully"
                                        " updated"),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

        else:
            print("Pkey validation error")

    def default_height():
        if get_user_profile(maindb):
            return get_user_profile(maindb)['height']

    def default_fedacct():
        return get_federation_account()
