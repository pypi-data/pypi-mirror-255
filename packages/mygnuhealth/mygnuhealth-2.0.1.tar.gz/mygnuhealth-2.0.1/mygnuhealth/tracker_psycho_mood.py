from kivy.uix.screenmanager import Screen
import datetime
from uuid import uuid4
from kivy.properties import ObjectProperty
from kivy.core.image import Image as CoreImage
from mygnuhealth.core import maindb, PageOfLife, line_plot


class TrackerPsychoMoodScreen(Screen):
    """Class that manages the person psychological related readings
        We set and retrieve the latest values from the psycho
        subsystem (mood and energy)

        Attributes:
        -----------

        Methods:
        --------
            set_values: Places the new reading values on the mood
                        and energy, and creates the
                        associated page of life

            read_mood: Retrieves the BP history
            getMood: Extracts the latest readings from the mood table
    """

    def read_mood():
        # Retrieve the  history
        mood_table = maindb.table('mood')
        moodhist = mood_table.all()
        return moodhist

    def getMood():
        # Extracts the latest readings from mood table (both mood and energy)
        moodhist = TrackerPsychoMoodScreen.read_mood()
        moodobj = ['', '', '']  # Init to empty string to avoid undefined val
        if moodhist:
            mood = moodhist[-1]  # Get the latest (newest) record
            dateobj = datetime.datetime.fromisoformat(mood['timestamp'])
            date_repr = dateobj.strftime("%a, %b %d '%y - %H:%M")
            moodobj = [str(date_repr), str(mood['mood']), str(mood['energy'])]

        return moodobj

    def set_values(self, mood, energy, information):
        mood_table = maindb.table('mood')
        current_date = datetime.datetime.now().isoformat()
        moodmon = False  # Init to false the mood monitoring process
        domain = 'medical'
        context = 'self_monitoring'

        if (energy > -1):  # Will evaluate to True since energy lower lim = 0
            moodmon = True
            mood_event_id = str(uuid4())
            synced = False
            mood_table.insert({'timestamp': current_date,
                               'event_id': mood_event_id,
                               'synced': synced,
                               'mood': mood,
                               'energy': energy})

            print("Saved Mood and Energy Levels", mood_event_id, synced, mood,
                  energy, current_date)

        if (moodmon):
            # This block is related to the Page of Life creation
            event_id = str(uuid4())
            monitor_readings = [
                {'mood_energy': {'mood': mood, 'energy': energy}},
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


class TrackerPsychoMoodStatsScreen(Screen):
    mood_plot = ObjectProperty()
    energy_plot = ObjectProperty()

    def on_pre_enter(self):
        # Update / Refresh the chart anytime we access the stats screen
        self.mood_plot, self.energy_plot = self.Moodplot()

    # Plotting - Mood and Energy
    def Moodplot(self):
        # Retrieves all the history and packages into an array.
        moodhist = TrackerPsychoMoodScreen.read_mood()
        mood = []
        energy = []
        mood_date = []

        # Sort the list of dictionaries using the timestamp as key
        sorted_list = sorted(moodhist, key=lambda sk: sk['timestamp'])

        for element in sorted_list:
            dateobj = datetime.datetime.fromisoformat(element['timestamp'])
            mood_date.append(dateobj)
            mood.append(element['mood'])
            energy.append(element['energy'])

        series_mood = {'Mood': mood}
        series_energy = {'Energy': energy}

        chart_mood = line_plot(title="Mood", series=series_mood,
                               x_values=None, y_legend='Mood')
        chart_energy = line_plot(title="Energy", series=series_energy,
                                 x_values=None, y_legend='Energy')

        return [CoreImage(chart_mood, ext="png").texture,
                CoreImage(chart_energy, ext="png").texture]
