from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import maindb, PageOfLife, line_plot


class TrackerBioGlucoseScreen(Screen):
    """Class that manages the person blood glucose readings

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the 'glucose'
            table and creates the associated page of life
            read_glucose: Retrieve the blood glucose levels history
            getGlucose: Extracts the latest readings from Glucose
    """

    def read_glucose():
        # Retrieve the blood glucose levels history
        glucose = maindb.table('glucose')
        glucosehist = glucose.all()
        return glucosehist

    def getGlucose():
        # Extracts the latest readings from Glucose
        glucosehist = TrackerBioGlucoseScreen.read_glucose()
        glucoseobj = ['', '']
        if (glucosehist):  # Enter this block if there is a history
            glucose = glucosehist[-1]  # Get the latest (newest) record
            dateobj = datetime.datetime.fromisoformat(glucose['timestamp'])
            date_repr = dateobj.strftime("%a, %b %d '%y - %H:%M")

            glucoseobj = [str(date_repr), str(glucose['glucose'])]
        return glucoseobj

    def validate_values(self, glucose):
        # Check for sanity on values before saving them
        rc = 0
        errors = []

        if glucose:
            if (int(glucose) in range(20, 800)):
                glucose = int(glucose)
            else:
                rc = -1
                errors.append("Glucose")
        else:
            glucose = 0

        if (rc == 0):
            self.set_values(glucose)

        else:
            popup = Popup(title='Wrong values',
                          content=Label(text=f"Plesae check {errors}"),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def set_values(self, blood_glucose):
        """Places the new reading values on the 'glucose' table

        Parameters
        ----------
        blood_glucose: value coming from the getvals method
        """

        glucose = maindb.table('glucose')
        current_date = datetime.datetime.now().isoformat()
        domain = 'medical'
        context = 'self_monitoring'

        if blood_glucose > 0:
            event_id = str(uuid4())
            synced = False
            monitor_vals = {'timestamp': current_date,
                            'event_id': event_id,
                            'synced': synced,
                            'glucose': blood_glucose
                            }
            glucose.insert(monitor_vals)

            print("Saved glucose", event_id, synced, blood_glucose,
                  current_date)

            # Create a new PoL with the values
            # within the medical domain and the self monitoring context
            pol_vals = {
                'page': event_id,
                'page_date': current_date,
                'domain': domain,
                'context': context,
                'measurements': [{'bg': blood_glucose}]
                }

            # Create the Page of Life associated to this blood glucose reading
            PageOfLife.create_pol(PageOfLife, pol_vals)


class TrackerBioGlucoseStatsScreen(Screen):
    glucose_plot = ObjectProperty()

    def on_pre_enter(self):
        # Update / Refresh the chart anytime we access the stats screen
        self.glucose_plot = self.Glucoseplot()

    # Plotting - Glycemia
    def Glucoseplot(self):
        # Retrieves the history and packages into an array.
        glucosehist = TrackerBioGlucoseScreen.read_glucose()
        glucose = []
        glucose_date = []
        sorted_list = sorted(glucosehist, key=lambda sk: sk['timestamp'])

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element['timestamp'])
            glucose_date.append(dateobj)
            glucose.append(element['glucose'])

        series_glucose = {'mg/dl': glucose}

        chart_io = line_plot(title='Blood Glucose Level',
                             series=series_glucose, y_legend='mg/dl',
                             x_values=None)

        return CoreImage(chart_io, ext="png").texture
