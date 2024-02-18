from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import maindb, PageOfLife, line_plot


class TrackerBioWeightScreen(Screen):
    """Class that manages the person weight readings

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the 'weight'
            and creates the associated page of life
            default_weight: Gets the latest weight (TODO replace by getWeight)
            read_weight: Retrieve the weight levels history
            getWeight: Extracts the latest readings from Weight
    """

    def default_weight(self):
        weighttable = maindb.table('weight')
        if (len(weighttable) > 0):
            last_weight = weighttable.all()[-1]
            return (last_weight['weight'])
        else:
            return 0

    def read_weight():
        # Retrieve the weight levels history
        weighttable = maindb.table('weight')
        weighthist = weighttable.all()
        return (weighthist)

    def getWeight():
        # Extracts the latest readings from Weight
        weighthist = TrackerBioWeightScreen.read_weight()
        weightobj = ['', '']
        if (weighthist):
            weight = weighthist[-1]  # Get the latest (newest) record
            dateobj = datetime.datetime.fromisoformat(weight['timestamp'])
            date_repr = dateobj.strftime("%a, %b %d '%y - %H:%M")

            weightobj = [str(date_repr), str(weight['weight'])]
        return weightobj

    def validate_values(self, body_weight):
        # Check for sanity on values before saving them
        rc = 0
        errors = []

        if body_weight:
            if (2 <= float(body_weight) < 500):
                body_weight = float(body_weight)
            else:
                print("Wrong value for weight")
                rc = -1
                errors.append("Body weight")
        else:
            body_weight = 0
            print("No weight")

        if (rc == 0):
            self.set_values(body_weight)

        else:
            popup = Popup(title='Wrong values',
                          content=Label(text=f"Plesae check {errors}"),
                          size_hint=(0.5, 0.5), auto_dismiss=True)
            popup.open()

    def set_values(self, body_weight):
        weighttable = maindb.table('weight')
        profiletable = maindb.table('profile')
        current_date = datetime.datetime.now().isoformat()
        domain = 'medical'
        context = 'self_monitoring'

        if body_weight > 0:
            event_id = str(uuid4())
            synced = False
            height = None
            bmi = None
            if (len(profiletable) > 0):
                height = profiletable.all()[0]['height']
            vals = {'timestamp': current_date,
                    'event_id': event_id,
                    'synced': synced,
                    'weight': body_weight}
            measurements = {'wt': body_weight}

            # If height is in the person profile, calculate the BMI
            if height:
                bmi = body_weight/((height/100)**2)
                bmi = round(bmi, 1)  # Use one decimal
                vals['bmi'] = bmi
                measurements['bmi'] = bmi

            weighttable.insert(vals)

            print("Saved weight", event_id, synced, body_weight, bmi,
                  current_date)

            # Create a new PoL with the values
            # within the medical domain and the self monitoring context
            pol_vals = {
                'page': event_id,
                'page_date': current_date,
                'domain': domain,
                'context': context,
                'measurements': [measurements]
                }

            # Create the Page of Life associated to this reading
            PageOfLife.create_pol(PageOfLife, pol_vals)


class TrackerBioWeightStatsScreen(Screen):
    weight_plot = ObjectProperty()

    def on_pre_enter(self):
        # Update / Refresh the chart anytime we access the stats screen
        self.weight_plot = self.Weightplot()

    # Plotting - Weight
    def Weightplot(self):
        # Retrieves the history and packages into an array.
        weighthist = TrackerBioWeightScreen.read_weight()
        weight = []
        weight_date = []
        sorted_list = sorted(weighthist, key=lambda sk: sk['timestamp'])

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element['timestamp'])
            weight_date.append(dateobj)
            weight.append(element['weight'])

        series_weight = {'Kg': weight}

        chart_io = line_plot(title='Weight',
                             series=series_weight, y_legend='Kg',
                             x_values=None)

        return CoreImage(chart_io, ext="png").texture
