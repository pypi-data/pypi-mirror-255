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

from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import maindb
from mygnuhealth.fedlogin import test_federation_connection as fc


class NetworkSettings():
    fed_table = maindb.table('federation')
    fedinfo = {}

    # Cast to dict the resulting tinydb.table.Document
    if (len(fed_table) > 0):
        fedinfo = dict(fed_table.all()[0])

    def update_federation_info(protocol, federation_server,
                               federation_port, enable_sync):

        # If the "Singleton" table is empty, insert, otherwise, update
        # TODO: Use upsert with doc_id == 1 as condition
        if not len(NetworkSettings.fed_table):
            NetworkSettings.fed_table.insert(
                {'protocol': protocol,
                 'federation_server': federation_server,
                 'federation_port': federation_port,
                 'enable_sync': enable_sync})
        else:
            NetworkSettings.fed_table.update(
                {'protocol': protocol,
                 'federation_server': federation_server,
                 'federation_port': federation_port,
                 'enable_sync': enable_sync})

    def test_connection(protocol, *args):
        conn_res = fc(protocol, *args)
        msg = "Unknown error"

        if (conn_res == 0):
            msg = "Connection OK"
        if (conn_res == -1):
            msg = "Invalid Credentials"
        if (conn_res == -2):
            msg = "Network Error"

        status_msg = f"{msg} (rc:{conn_res})"
        popup = Popup(title='Federation Connection Status',
                      content=Label(text=status_msg),
                      size_hint=(0.5, 0.5), auto_dismiss=True)
        popup.open()

        return [conn_res, msg]
