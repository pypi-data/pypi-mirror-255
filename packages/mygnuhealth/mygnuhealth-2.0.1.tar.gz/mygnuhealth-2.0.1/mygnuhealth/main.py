#!/usr/bin/env python3
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

import sys
import os
import logging
import kivy
import mygnuhealth.about as about
from mygnuhealth.user_account import UserAccount

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, ListProperty, DictProperty

# Import some of the screens from their own module files
from mygnuhealth.tracker_bio_cardio import TrackerBioCardioScreen as cardio
from mygnuhealth.tracker_bio_glucose import TrackerBioGlucoseScreen as glucose
from mygnuhealth.tracker_bio_weight import TrackerBioWeightScreen as weight
from mygnuhealth.tracker_bio_osat import TrackerBioOsatScreen as osat

from mygnuhealth.tracker_lifestyle_pactivity import \
    TrackerLifestylePactivityScreen as pactivity
from mygnuhealth.tracker_lifestyle_nutrition import \
    TrackerLifestyleNutritionScreen as nutrition

from mygnuhealth.tracker_lifestyle_sleep import TrackerLifestyleSleepScreen \
     as sleep

from mygnuhealth.tracker_lifestyle_social import TrackerLifestyleSocialScreen \
     as social_activity

from mygnuhealth.tracker_psycho_mood import TrackerPsychoMoodScreen \
     as mood

from mygnuhealth.profile_settings import ProfileSettings as profile

from mygnuhealth.network_settings import NetworkSettings as network

from mygnuhealth.book_of_life import BookofLife as bol

from mygnuhealth.page_of_life import PoL as pol

kivy.require('2.3.0')


""" By default Kivy looks for the file name that
    of the same as the main class (MyGNUHealthApp) in
    lower case and without the App suffix, "so mygnuhealth.kv"

    We want to place the user interface in the ui directory, so
    we'll use the Builder load_file method for that.
"""
moddir = os.path.dirname(os.path.abspath(__file__))

# Change directory to this module cwd so we can invoke the images
# and other files relative to it.
os.chdir(moddir)


class Menu(BoxLayout):
    manager = ObjectProperty(None)


# Declare the screens
class InitialScreen(Screen):
    """ In this initial class, MyGNUHealth checks if the
        user account has been created. If that is the case
        the next screen will be the login screen.
        If the user does not exist, it will take them to the
        user account initial setup wizard.
    """

    def account_status(self):
        acct = UserAccount()
        account = acct.account_exist()
        if account:
            self.manager.current = "login"
        else:
            self.manager.current = "newuser"


class LoginScreen(Screen):

    personal_key = ObjectProperty()

    def validate_credentials(self):
        # Check userid
        acct = UserAccount()
        if acct.login(self.personal_key.text):
            logging.info("Welcome to the jungle!")
            App.get_running_app().login_status = True
            self.manager.current = "phr"

        else:
            # switching the current screen to display validation result
            logging.error("Wrong key")

            popup = Popup(title='Invalid Credentials',
                          content=Label(text='Wrong Personal key'),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

            # reset the personal key
            self.personal_key.text = ""


class NewUserScreen(Screen):

    def init_user(self, username, sex, height, bday,
                  bmonth, byear, pkey, pkey_repeat):
        birthdate = [byear, bmonth, bday]
        acct = UserAccount()

        if (acct.createAccount(pkey, pkey_repeat,
                               height, username, birthdate, sex)):
            self.manager.current = "login"


class AboutScreen(Screen):
    myghinfo = about


class PHRScreen(Screen):
    pass


class HealthTrackerScreen(Screen):
    pass


class ProfileSettingsScreen(Screen):
    person_height = ObjectProperty()
    person_fedacct = ObjectProperty()

    person_profile = profile

    def on_pre_enter(self):
        # Get the default values for height and federation account
        self.person_height = profile.default_height()
        self.person_fedacct = profile.default_fedacct()


class NetworkSettingsScreen(Screen):
    # Default information of the thalamus server
    thalamus = DictProperty({
        'federation_account': '',
        'protocol': 'https',
        'federation_server': '',
        'federation_port': 8443,
        'enable_sync': False})

    network_settings = network

    def on_pre_enter(self):
        # Get the values from the current network settings
        self.thalamus = self.network_settings.fedinfo


class TrackerBioScreen(Screen):
    bp = ListProperty(["", "", "", ""])  # Date, sys, dia and hr
    glucose = ListProperty(["", ""])     # Date and glycemia value
    weight = ListProperty(["", ""])     # Date and weight value
    osat = ListProperty(["", ""])     # Date and osat value

    def on_pre_enter(self):
        # Refresh the chart anytime we access the bio summary
        self.bp = cardio.getBP()
        self.glucose = glucose.getGlucose()
        self.weight = weight.getWeight()
        self.osat = osat.getOsat()


class PageofLifeScreen(Screen):
    pdate = ListProperty(["", "", "", "", ""])  # Year, month, day, hour, min
    domains = ListProperty()
    domain_contexts = ListProperty()
    rsinfo = DictProperty(
        {'dbsnp': '', 'gene': '', 'protein': '', 'variant': '',
         'aa_change': '', 'category': '', 'disease': ''})

    page = pol

    def on_pre_enter(self):
        self.pdate = pol.get_date()
        self.domains = pol.get_domains()

    def get_domain_contexts(self, domain):
        self.domain_contexts = pol.get_contexts(domain)

    def get_rsinfo(self, rs):
        if (rs):
            res = pol.checkSNP(rs)
            if res:
                self.rsinfo = res
            else:
                # Reset to '' all the rsinfo dictionary key values
                self.rsinfo = dict.fromkeys(self.rsinfo, '')


class BookofLifeScreen(Screen):
    bolgrid = ObjectProperty()
    book = ListProperty([])

    bookcls = bol

    def on_pre_enter(self):
        pols = bol.read_book()
        # Refresh the chart anytime we access the bio summary
        for page in pols:
            page_date = f'[color=#32393a]{str(page["date"])}[/color]\n'
            page_domain = f'[color=#32393a]{str(page["domain"])}[/color]\n'
            page_summary = f'[color=#32393a]{str(page["summary"])}[/color]\n'

            self.bolgrid.add_widget(Label(text=page_date, markup=True))
            self.bolgrid.add_widget(Label(text=page_domain, markup=True))
            self.bolgrid.add_widget(Label(text=page_summary, markup=True))
        print(f'Number of pages {len(pols)}')


class TrackerLifestyleScreen(Screen):
    # Date, aerobic, anaerobic, steps
    pactivity = ListProperty(["", "", "", ""])
    # Date, morning, afternoon, evening, total, info
    nutrition = ListProperty(["", "", "", "", ""])
    # Date, sleep_time, quality, info
    sleep = ListProperty(["", "", "", ""])
    # Date, meaningful social activities time, info
    social_activity = ListProperty(["", "", ""])

    def on_pre_enter(self):
        # Refresh the chart anytime we access the lifestyle summary
        self.pactivity = pactivity.getPA()
        self.nutrition = nutrition.getNutrition()
        self.sleep = sleep.getSleep()
        self.social_activity = social_activity.getSA()


class TrackerPsychoScreen(Screen):
    # Date, mood, energy, info
    mood = ListProperty(["", "", "", ""])

    def on_pre_enter(self):
        # Refresh the chart anytime we access the lifestyle summary
        self.mood = mood.getMood()


class ScreenController(ScreenManager):
    pass


# Load the main kv file from the UI directory
# call load_file from here, after all the classes are declared
kv = Builder.load_file('ui/mygnuhealth.kv')

""" By default Kivy looks for the file name that
    of the same as the main class (MyGNUHealthApp) in
    lower case and without the "App" suffix, "so mygnuhealth.kv"
    We use the Builder load_file method to call it from the ui dir
"""


class MyGnuHealthApp(App):
    # Use a soft background color
    # Window.clearcolor = get_color_from_hex('#f5fafa')
    Window.clearcolor = get_color_from_hex('#ffffff')

    """ The last_known_screen keeps the latest loaded screen.
        We use this variable for return to the previous screen
        as in the the About page (similar to a stack pop operation)
    """
    last_known_screen = None
    login_status = False

    def build(self):
        self.title = f"MyGNUHealth {about.__version__}"
        self.icon = 'images/mygnuhealth-icon.png'
        return Menu()

    def bailout(self, rc):
        """ Exit the application with the given return code, rc
        """
        sys.exit(rc)


def mygh():
    MyGnuHealthApp().run()


if __name__ == "__main__":
    mygh()
