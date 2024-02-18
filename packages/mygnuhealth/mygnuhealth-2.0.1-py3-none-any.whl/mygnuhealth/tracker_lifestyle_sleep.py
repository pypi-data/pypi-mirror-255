from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import maindb, PageOfLife, line_plot


class TrackerLifestyleSleepScreen(Screen):
    """ Class that manages the person Sleep related readings
        We set and retrieve the latest values from the sleep
        subsystem (time and quality)

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the sleep
                        and creates the associated page of life

    """

    # SLEEP
    def read_sleep():
        # Retrieve the sleep history
        sleep = maindb.table('sleep')
        sleephist = sleep.all()
        return sleephist

    def getSleep():
        # Extracts the latest readings from the sleep table
        sleephist = TrackerLifestyleSleepScreen.read_sleep()
        # date, hours, sleep quality
        sleepobj = ['', '', '']
        if sleephist:
            sleep = sleephist[-1]  # Get the latest (newest) record

            dateobj = datetime.datetime.fromisoformat(sleep['timestamp'])
            date_repr = dateobj.strftime("%a, %b %d '%y - %H:%M")

            sleepobj = [str(date_repr), str(sleep['sleeptime']),
                        str(sleep['sleepquality'])]

        return sleepobj

    def validate_values(self, sleeptime, sleepquality, information):
        # Check for sanity on values before saving them
        rc = 0
        errors = []
        if sleeptime:
            if (0.1 <= float(sleeptime) <= 23.5):
                sleeptime = float(sleeptime)
            else:
                rc = -1
                errors.append("Sleep time")
        else:
            sleeptime = 0

        if (rc == 0):
            self.set_values(sleeptime, sleepquality, information)

        else:
            popup = Popup(title='Wrong values',
                          content=Label(text=f"Please check {errors}"),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def set_values(self, sleeptime, sleepquality, information):
        sleep = maindb.table('sleep')
        current_date = datetime.datetime.now().isoformat()
        domain = 'lifestyle'
        context = 'sleep'

        sleep_event_id = str(uuid4())
        synced = False
        sleep.insert({'timestamp': current_date,
                      'event_id': sleep_event_id,
                      'synced': synced,
                      'sleeptime': sleeptime,
                      'sleepquality': sleepquality})

        print("Saved Sleep information", sleep_event_id,
              sleeptime, sleepquality, current_date)

        # Page of Life block related to Sleep
        event_id = str(uuid4())
        monitor_readings = [
            {'sleep': {'sleeptime': sleeptime,
                       'sleepquality': sleepquality}},
            ]

        pol_vals = {
            'page': event_id,
            'page_date': current_date,
            'domain': domain,
            'context': context,
            'measurements': monitor_readings,
            'info': information
            }

        # Create the Page of Life associated to this reading
        PageOfLife.create_pol(PageOfLife, pol_vals)


class TrackerLifestyleSleepStatsScreen(Screen):
    sleep_plot = ObjectProperty()

    def on_pre_enter(self):
        # Update / Refresh the chart anytime we access the stats screen
        self.sleep_plot = self.Sleepplot()

    # Plotting - Sleep
    def Sleepplot(self):
        # Retrieves all the history and packages into an array.
        sleephist = TrackerLifestyleSleepScreen.read_sleep()
        sleep_time = []
        sleep_date = []

        # Sort the list of dictionaries using the timestamp as key
        sorted_list = sorted(sleephist, key=lambda sk: sk['timestamp'])

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element['timestamp'])
            sleep_date.append(dateobj)
            sleep_time.append(element['sleeptime'])

        series_sleep = {'Sleep': sleep_time}

        chart_io = line_plot(title='Sleep', series=series_sleep,
                             y_legend='Hours', x_values=None)

        return CoreImage(chart_io, ext="png").texture
