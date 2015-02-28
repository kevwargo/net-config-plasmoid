#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
from PyKDE4.kdeui import *
import time

import json
from PyKDE4.kdecore import i18n
from restkit import request

# remote server (must put that in the plasmoid config later...)
SERVER = 'http://localhost:5000/api'
# remote uri
GET_TICKETS = SERVER + '/tickets/pigeot_j/'
SEND_TICKET = SERVER + '/tickets/pigeot_j/'
GET_ASKERS =  SERVER + '/users/askers/'
GET_RECEIVERS = SERVER + '/users/receivers/'
GET_GROUPS =  SERVER + '/groups/'
     
class NotificationPlasmaApplet(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)

    def init(self):
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.Square)
        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        self.setBackgroundHints(Plasma.Applet.DefaultBackground)
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.layout1 = QGraphicsLinearLayout(Qt.Vertical)
        # self.changeConfButton = Plasma.PushButton(self.applet)
        # self.onOffButton = Plasma.PushButton(self.applet)

        
        self.button = Plasma.PushButton()
        self.button.setText("hello")
        self.connect(self.button, SIGNAL("clicked()"), self.notify)
        self.layout.addItem(self.button)
        self.applet.setLayout(self.layout)

    def notify(self):
        # print "notify"
        print self.applet, self
        # self.layout.removeItem(self.labelFirstHeader)
        self.labelFirstHeader = Plasma.Label()
        self.labelFirstHeader.setText("LEPECBEKE")
        self.layout1 = QGraphicsLinearLayout(Qt.Vertical)
        self.layout1.addItem(self.labelFirstHeader)
        self.applet.setLayout(self.layout1)


class GLPIApplet(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)

    def init(self):
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.Square)
        self.resize(400,650)
        # new ticket button
        self.new = Plasma.PushButton()
        self.new.setText('Nouveau Ticket')
        self.connect(self.new, SIGNAL('clicked()'), self.new_ticket_ui)
        # refresh button
        self.refresh = Plasma.PushButton()
        self.refresh.setText('Rafraichir')
        self.connect(self.refresh, SIGNAL('clicked()'), self.view_tickets_ui)
        # coming back button
        self.back = Plasma.PushButton()
        self.back.setText('Retour')
        self.connect(self.back, SIGNAL('clicked()'), self.view_tickets_ui)
        # saving a ticket button
        self.send_ticket = Plasma.PushButton()
        self.send_ticket.setText('Enregistrer le ticket')
        self.connect(self.send_ticket, SIGNAL('clicked()'), self.save_ticket)
        # initialize
        self.view_tickets_ui()

    def view_tickets(self):
        # shows the tickets of the user
        results = self.fetch_tracking('%s' % GET_TICKETS)
        if results:
            trackings = results['trackings']['content']
            if len(trackings) > 5:
                trackings = trackings[0:4]
            tickets = []
            for tracking in trackings:
                id = tracking['id']
                name = tracking['name']
                date = tracking['date']
                author = tracking['author']
                data = u'%s (%s)' % (name, author)
                label = Plasma.Label()
                label.setText(data)
                tickets.append(label)
            for ticket in tickets:
                self.layout.addItem(ticket)
        else:
            print "cannot connect to the given uri..."
            data = u'pas de résultat'
            self.label = Plasma.Label()
            self.label.setText(data)
            self.layout.addItem(self.label)

    def view_ticket(self):
        # shows the given ticket
        print "ticket demande"
        pass

    def fetch_tracking(self, resource):
        # let getting the asked resource
        try:
            response = request(resource)
            html = response.body_string()
            result = json.loads(html)
            response.close()
        except:
            result = None
        return result

    def view_tickets_ui(self, message=None):
        # layout of ticket view
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.layout.itemSpacing(3)
        if message:
            message_label = Plasma.Label()
            message_label.setText('%s' % message)
            self.layout.addItem(message_label)
        self.layout.addItem(self.new)
        self.view_tickets()
        self.layout.addItem(self.refresh)
        self.applet.setLayout(self.layout)

    def new_ticket_ui(self, message=None):
        # layout of a new ticket
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.layout.itemSpacing(3)
        ## display the message if present
        if message:
            message_label = Plasma.Label()
            message_label.setText('%s' % message)
            self.layout.addItem(message_label)
        ## declaration des items:
        # asker
        demandeur_label = Plasma.Label()
        demandeur_label.setText('Demandeur:')
        demandeur = Plasma.ComboBox()
        demandeur.addItem("")
        self.populate_user(demandeur, '%s' % GET_ASKERS)
        # receiver
        destinataire_label = Plasma.Label()
        destinataire_label.setText('Destinataire:')
        destinataire = Plasma.ComboBox()
        destinataire.addItem("")
        self.populate_user(destinataire, '%s' % GET_RECEIVERS)
        # receiver group
        gdestinataire_label = Plasma.Label()
        gdestinataire_label.setText('Groupe Destinataire:')
        gdestinataire = Plasma.ComboBox()
        gdestinataire.addItem("")
        self.populate_group(gdestinataire, '%s' % GET_GROUPS)
        # title
        line_edit = Plasma.LineEdit()
        line_edit.nativeWidget().setClearButtonShown(True)
        line_edit.nativeWidget().setClickMessage(i18n("Entrez le titre du ticket ici"))
        # description
        text_edit = Plasma.TextEdit()
        text_edit.nativeWidget().setClickMessage(i18n("Description"))
        text1 = Plasma.TextBrowser()
        text2 = Plasma.TabBar()
        # adding the items:
        self.layout.addItem(self.back)
        self.layout.addItem(demandeur_label)
        self.layout.addItem(demandeur)
        self.layout.addItem(destinataire_label)
        self.layout.addItem(destinataire)
        self.layout.addItem(gdestinataire_label)
        self.layout.addItem(gdestinataire)
        self.layout.addItem(line_edit)
        self.layout.addItem(text_edit)
        self.layout.addItem(text1)
        self.layout.addItem(text2)
        self.layout.addItem(self.send_ticket)
        self.applet.setLayout(self.layout)

    def detail_ticket_ui(self):
        # view of a ticket
        print 'detail ticket'
        self.layout = QGraphicsLinearLayout(Qt.Vertical)
        self.layout.itemSpacing(3)
        self.layout.addItem(self.back)
        self.applet.setLayout(self.layout)

    def save_ticket(self):
        # saving a ticket
        status = 0
        try:
            ticket = request('%s' % SEND_TICKET,'POST',
                {'data': 'dataaaaa'})
            response = ticket.body_stream()
            data = response.readlines()[3]
            status = ticket.status_int
        except:
            print "impossible d'envoyer le ticket"

        if status == '200':
            self.view_tickets_ui(u'ticket bien envoyé')
        else:
            self.new_ticket_ui('code http %i : %s' % (status, data))

    def populate_user(self, combobox, resource):
        # populate the given combobox with user infos from the given uri
        results = self.fetch_tracking(resource)
        if results:
            users = results['users']['content']
            users_final = []
            for user in users:
                id = user['id']
                login = user['login']
                name = user['name']
                combobox.addItem(name)
        else:
            combobox.addItem('impossible de trouver les utilisateurs')

    def populate_group(self, combobox, resource):
        # populate the given combobox with group infos from the given uri
        results = self.fetch_tracking(resource)
        if results:
            groups = results['groups']['content']
            for group in groups:
                id = group['id']
                name = group['name']
                combobox.addItem(name)
        else:
            combobox.addItem('impossible d\'afficher les groupes')


def CreateApplet(parent):
    return NotificationPlasmaApplet(parent)
    # return GLPIApplet(parent)
