####################################################################
#   Copyright (C) 2020-2024 Luis Falcon <falcon@gnuhealth.org>
#   Copyright (C) 2020-2024 GNU Solidario <health@gnusolidario.org>
#   License: GPL v3+
#   Please read the COPYRIGHT and LICENSE files of the package
####################################################################

import datetime
from tinydb import Query
from uuid import uuid4
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.core import check_date, PageOfLife, vardb


class PoL():
    """This class creates a new page in the user's Book of Life

        Attributes:
        -----------
            wrongDate: Signal to emit when an invalid date is found
            todayDate: Property with current date

        Methods:
        --------
            get_domains: Returns main domains (medical, social, biographical..)

    """

    def get_rsinfo(self):
        return self.rsinfo

    def get_domains():
        # Return a the list of domains (the value)
        # TODO: In widgets like spinner, we should be able to show the text
        # for translation
        domain = []
        for d in PageOfLife.pol_domain:
            domain.append(d['value'])
        return domain

    def get_contexts(domain):
        contexts = []
        if domain == 'social':
            domain_contexts = PageOfLife.social_context
        if domain == 'medical':
            domain_contexts = PageOfLife.medical_context
        if domain == 'lifestyle':
            domain_contexts = PageOfLife.lifestyle_context
        if domain == 'biographical':
            domain_contexts = PageOfLife.biographical_context
        if domain == 'other':
            domain_contexts = PageOfLife.other_context

        for c in domain_contexts:
            contexts.append(c['value'])
        return contexts

        return domain_contexts

    def update_context(self, domain):
        """ Set the value of the domain from the selection"""
        if domain == 'social':
            self.pol_context = PageOfLife.social_context
        if domain == 'medical':
            self.pol_context = PageOfLife.medical_context
        if domain == 'lifestyle':
            self.pol_context = PageOfLife.lifestyle_context
        if domain == 'biographical':
            self.pol_context = PageOfLife.biographical_context
        if domain == 'other':
            self.pol_context = PageOfLife.other_context
        # Emit the change of domain, so it updates the context
        self.domainChanged.emit()

        return self.pol_context

    def get_date():
        """
        Returns the date packed into an array (day,month,year, hour, min)
        """
        rightnow = datetime.datetime.now()
        dateobj = []
        dateobj.append(str(rightnow.day))
        dateobj.append(str(rightnow.month))
        dateobj.append(str(rightnow.year))
        dateobj.append(str(rightnow.hour))
        dateobj.append(str(rightnow.minute))
        return dateobj

    def new_page(data):
        page_id = str(uuid4())

        pol_vals = {
            'page': page_id,
            'page_date': data['page_date'],
            'domain': data['domain'],
            'context': data['context'],
            'relevance': data['relevance'],
            'privacy': data['privacy'],
            'summary': data['summary'],
            'info': data['info']
            }
        if (data['context'] == 'genetics'):
            pol_vals.update({'genetic_info': data['genetic_info']})

        PageOfLife.create_pol(PageOfLife, pol_vals)

    def checkSNP(rs):
        rsinfo = {}
        if rs:
            Rsnp = Query()
            res = vardb.search(Rsnp.dbsnp == rs)
            if len(res) > 0:
                res = res[0]
                rsinfo = {
                        'rsid': res['dbsnp'],
                        'gene': res['gene'],
                        'aa_change': res['aa_change'],
                        'variant': res['variant'],
                        'protein': res['protein'],
                        'category': res['category'],
                        'disease': res['disease']
                        }

                print(rsinfo)
            else:
                print(f"{rs} not found")

        return (rsinfo)

    def createPage(page_date, domain, context, relevance, private_page,
                   genetic_info, summary, info):
        # Retrieves the information from the initialization form
        # Creates the page from the information on the form
        if (page_date):
            if (check_date(page_date[:3])):
                # Sets the page of life date and time
                year, month, day, hour, minute = page_date
                daterp = str(datetime.datetime(int(year), int(month),
                             int(day), int(hour), int(minute)))
                page = {'page_date': daterp,
                        'domain': domain,
                        'context': context,
                        'relevance': relevance,
                        'privacy': private_page,
                        'summary': summary,
                        'info': info
                        }
                if (context == 'genetics'):
                    rsinfo = {
                        'rsid': genetic_info[0],
                        'gene': genetic_info[1],
                        'aa_change': genetic_info[2],
                        'variant': genetic_info[3],
                        'protein': genetic_info[4],
                        'significance': genetic_info[5],
                        'disease': genetic_info[6]
                        }
                    page.update({'genetic_info': rsinfo})
                PoL.new_page(page)
                popup = Popup(title='Success',
                              content=Label(text="Page of Life"
                                            " successfully created!"),
                              size_hint=(0.5, 0.5), auto_dismiss=True)
                popup.open()
                return True

            else:
                popup = Popup(title='Error',
                              content=Label(text="Wrong date"),
                              size_hint=(0.5, 0.5), auto_dismiss=True)
                popup.open()

