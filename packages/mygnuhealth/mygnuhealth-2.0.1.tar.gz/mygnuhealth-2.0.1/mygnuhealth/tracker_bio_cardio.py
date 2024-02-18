from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import maindb, PageOfLife, line_plot


class TrackerBioCardioScreen(Screen):
    """Class that manages the person cardio related readings
        We set and retrieve the latest values from the cardio
        subsystem (blood pressure  and heart rate)

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the blood
                        pressure and heart rate, and creates the
                        associated page of life

            read_bp: Retrieves the BP history
            read_hr: Retrieves the HR history
            getBP: Extracts the latest readings from BP
    """

    def read_bp():
        # Retrieves the BP history
        blood_pressure = maindb.table('bloodpressure')
        bphist = blood_pressure.all()
        return bphist

    def read_hr():
        # Retrieves the HR history
        hr = maindb.table('heart_rate')
        hrhist = hr.all()
        return (hrhist)

    def getBP():
        # Extracts the latest readings from BP
        bphist = TrackerBioCardioScreen.read_bp()
        hrhist = TrackerBioCardioScreen.read_hr()
        bpobj = ['', '', '', '']  # Init to empty string to avoid undefined val
        if bphist and hrhist:
            bp = bphist[-1]  # Get the latest (newest) record
            hr = hrhist[-1]
            dateobj = datetime.datetime.fromisoformat(bp['timestamp'])
            date_repr = dateobj.strftime("%a, %b %d '%y - %H:%M")

            bpobj = [str(date_repr), str(bp['systolic']), str(bp['diastolic']),
                     str(hr['heart_rate'])]

        return bpobj

    def validate_values(self, systolic, diastolic, heart_rate):
        # Check for sanity on values before saving them
        rc = 0
        errors = []
        if systolic:
            if (int(systolic) in range(20, 300)):
                systolic = int(systolic)
            else:
                rc = -1
                errors.append("Systolic")
        else:
            systolic = 0

        if diastolic:
            if (int(diastolic) in range(20, 300)):
                diastolic = int(diastolic)
            else:
                errors.append("Diastolic")
                rc = -1
        else:
            diastolic = 0

        if heart_rate:
            if (int(heart_rate) in range(20, 400)):
                heart_rate = int(heart_rate)
            else:
                print("Wrong value for heart_rate")
                rc = -1
                errors.append("Heart rate")
        else:
            heart_rate = 0
            print("No heart rate")

        if (rc == 0):
            self.set_values(systolic, diastolic, heart_rate)

        else:
            popup = Popup(title='Wrong values',
                          content=Label(text=f"Plesae check {errors}"),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def set_values(self, systolic, diastolic, heart_rate):
        blood_pressure = maindb.table('bloodpressure')
        hr = maindb.table('heart_rate')
        current_date = datetime.datetime.now().isoformat()
        bpmon = hrmon = False  # Init to false the bp and hr monitoring process
        domain = 'medical'
        context = 'self_monitoring'

        if (systolic > 0) and (diastolic > 0):
            bpmon = True
            bp_event_id = str(uuid4())
            synced = False
            blood_pressure.insert({'timestamp': current_date,
                                   'event_id': bp_event_id,
                                   'synced': synced,
                                   'systolic': systolic,
                                   'diastolic': diastolic})

            print("Saved blood pressure", bp_event_id, synced, systolic,
                  diastolic, current_date)

        if heart_rate > 0:
            hrmon = True
            hr_event_id = str(uuid4())
            synced = False
            hr.insert({'timestamp': current_date,
                       'event_id': hr_event_id,
                       'synced': synced,
                       'heart_rate': heart_rate})

            print("Saved Heart rate", hr_event_id, synced,
                  heart_rate, current_date)

        if (bpmon or hrmon):
            # This block is related to the Page of Life creation
            if (bpmon and hrmon):
                # Group both HR and BP monitors in one PoL if both readings
                # where taken at the same moment / device
                # The event_id will be unique
                event_id = str(uuid4())
                monitor_readings = [
                    {'bp': {'systolic': systolic, 'diastolic': diastolic}},
                    {'hr': heart_rate}
                    ]
            elif (bpmon and not hrmon):
                event_id = bp_event_id
                monitor_readings = [
                    {'bp': {'systolic': systolic, 'diastolic': diastolic}},
                    ]
            else:
                event_id = hr_event_id
                monitor_readings = [{'hr': heart_rate}]

            pol_vals = {
                'page': event_id,
                'page_date': current_date,
                'domain': domain,
                'context': context,
                'measurements': monitor_readings
                }

            # Create the Page of Life associated to this reading
            PageOfLife.create_pol(PageOfLife, pol_vals)


class TrackerBioCardioStatsScreen(Screen):
    hr_plot = ObjectProperty()
    bp_plot = ObjectProperty()

    def on_pre_enter(self):
        # Update / Refresh the chart anytime we access the stats screen
        self.hr_plot = self.HRplot()
        self.bp_plot = self.BPplot()

    # Plotting - Heart rate
    def HRplot(self):
        # Retrieves all the history and packages into an array.
        hrhist = TrackerBioCardioScreen.read_hr()
        hr = []
        hr_date = []
        sorted_list = sorted(hrhist, key=lambda sk: sk['timestamp'])

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element['timestamp'])
            hr_date.append(dateobj)
            hr.append(element['heart_rate'])

        series_hr = {'Heart Rate': hr}

        # chart_io = line_plot('Heart rate', 'BPM', hr, x_values=None)
        chart_io = line_plot(title='Heart rate',
                             series=series_hr, y_legend='BPM',
                             x_values=None)

        return CoreImage(chart_io, ext="png").texture

    # Plotting - Blood Pressure
    def BPplot(self):
        # Retrieves all the history and packages into an array.
        bphist = TrackerBioCardioScreen.read_bp()
        bpsys = []
        bpdia = []
        bp_date = []

        # Sort the list of dictionaries using the timestamp as key
        sorted_list = sorted(bphist, key=lambda sk: sk['timestamp'])

        for element in sorted_list:

            dateobj = datetime.datetime.fromisoformat(element['timestamp'])
            bp_date.append(dateobj)
            bpsys.append(element['systolic'])
            bpdia.append(element['diastolic'])

        series_bp = {'Systolic': bpsys, 'Diastolic': bpdia}

        chart_io = line_plot(title='Blood Pressure',
                             series=series_bp, y_legend='mmHg',
                             x_values=None)

        return CoreImage(chart_io, ext="png").texture
