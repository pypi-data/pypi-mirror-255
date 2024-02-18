from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import maindb, PageOfLife, line_plot, stacked_plot


class TrackerLifestylePactivityScreen(Screen):
    """ Class that manages the person Physical Activity related readings
        We set and retrieve the latest values from the physical activity
        subsystem (aerobic, anaerobic and steps)

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the physical
                        activity and creates the associated page of life

    """

    # PHYSICAL ACTIVITY
    def read_pa():
        # Retrieve the physical activity history
        pactivity = maindb.table('physicalactivity')
        pahist = pactivity.all()
        return pahist

    def getPA():
        # Extracts the latest readings from Physical Activity table
        pahist = TrackerLifestylePactivityScreen.read_pa()
        paobj = ['', '', '', '']  # Init to empty string to avoid undefined val
        if pahist:
            pa = pahist[-1]  # Get the latest (newest) record

            dateobj = datetime.datetime.fromisoformat(pa['timestamp'])
            date_repr = dateobj.strftime("%a, %b %d '%y - %H:%M")

            paobj = [str(date_repr), str(pa['aerobic']),
                     str(pa['anaerobic']), str(pa['steps'])]

        return paobj

    def validate_values(self, aerobic, anaerobic, steps):
        # Check for sanity on values before saving them
        rc = 0
        errors = []
        if aerobic:
            if (int(aerobic) in range(1, 1400)):
                aerobic = int(aerobic)
            else:
                rc = -1
                errors.append("Aerobic")
        else:
            aerobic = 0

        if anaerobic:
            if (int(anaerobic) in range(1, 1400)):
                anaerobic = int(anaerobic)
            else:
                errors.append("Anaerobic")
                rc = -1
        else:
            anaerobic = 0

        if steps:
            if (int(steps) in range(1, 200000)):
                steps = int(steps)
            else:
                rc = -1
                errors.append("Steps")
        else:
            steps = 0

        if (rc == 0):
            self.set_values(aerobic, anaerobic, steps)

        else:
            popup = Popup(title='Wrong values',
                          content=Label(text=f"Plesae check {errors}"),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def set_values(self, aerobic, anaerobic, steps):
        pactivity = maindb.table('physicalactivity')
        current_date = datetime.datetime.now().isoformat()
        domain = 'lifestyle'
        context = 'physical_activity'

        pa_event_id = str(uuid4())
        synced = False
        pactivity.insert({'timestamp': current_date,
                          'event_id': pa_event_id,
                          'synced': synced,
                          'aerobic': aerobic,
                          'anaerobic': anaerobic,
                          'steps': steps})

        print("Saved Physical Activity", pa_event_id, synced, aerobic,
              anaerobic, steps, current_date)

        # Page of Life block related to Physical Activity
        event_id = str(uuid4())
        monitor_readings = [
            {'pa': {'aerobic': aerobic, 'anaerobic': anaerobic,
                    'steps': steps}},
            ]

        pol_vals = {
            'page': event_id,
            'page_date': current_date,
            'domain': domain,
            'context': context,
            'measurements': monitor_readings
            }

        # Create the Page of Life associated to this reading
        PageOfLife.create_pol(PageOfLife, pol_vals)


class TrackerLifestylePactivityStatsScreen(Screen):
    pa_plot = ObjectProperty()
    steps_plot = ObjectProperty()

    def on_pre_enter(self):
        # Update / Refresh the chart anytime we access the stats screen
        self.pa_plot, self.steps_plot = self.PAplot()

    # Plotting - Physical Activity
    def PAplot(self):
        # Retrieves all the history and packages into an array.
        pahist = TrackerLifestylePactivityScreen.read_pa()
        pa_aerobic = []
        pa_anaerobic = []
        pa_steps = []
        pa_date = []

        # Sort the list of dictionaries using the timestamp as key
        sorted_list = sorted(pahist, key=lambda sk: sk['timestamp'])

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element['timestamp'])
            pa_date.append(dateobj)
            pa_aerobic.append(element['aerobic'])
            pa_anaerobic.append(element['anaerobic'])
            pa_steps.append(element['steps'])

        series_pa = {'Aerobic': pa_aerobic, 'Anaerobic': pa_anaerobic}
        series_steps = {'Steps': pa_steps}

        chart_pa = stacked_plot('Physical Activity', series_pa, x_values=None)
        chart_steps = line_plot(title="Steps", series=series_steps,
                                x_values=None, y_legend='Steps')

        return [CoreImage(chart_pa, ext="png").texture,
                CoreImage(chart_steps, ext="png").texture]
