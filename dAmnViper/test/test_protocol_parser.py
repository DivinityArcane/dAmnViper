''' dAmnViper.test.test_protocol_parser module
    Created by photofroggy
    
    This module provides unit tests for testing the protocol parser found in
    dAmnViper.parse.
'''

from twisted.trial import unittest

from dAmnViper.parse import Packet
from dAmnViper.parse import ProtocolParser


class TestProtocolParser(unittest.TestCase):
    """ Unit tests for the protocol parser. """
    
    def setUp(self):
        self.parser = ProtocolParser()
        
    def test_event_name(self):
        """ Test the ``event_name`` method of the protocol parser. """
        # Basic part packet
        packet = Packet('recv chat:Botdom\n\npart photofroggy\nr=timed out')
        
        # event_name should return `recv_part` in this case!
        packet_name = self.parser.event_name(packet)
        
        self.failIf(packet_name != 'recv_part',
            'Protocol parser does not properly determine packet names')
    
    def test_event_name_unknown(self):
        """ Make sure the parser returns a correct value for an unknown packet. """
        # Unsupported packet.
        packet = Packet('foo bar\n')
        
        # event_name should return `unknown` in this case!
        packet_name = self.parser.event_name(packet)
        
        self.failIf(packet_name != 'unknown',
            'Protocol recognised an unsupported packet as a supported packet')
    
    def test_mapper(self):
        """ Test the ``mapper`` method of the protocol parser. """
        # Testing the mapper using a recv_msg packet has the side-effect
        # of testing both the generic_recv and sort methods.
        packet = Packet('recv chat:Botdom\n\nmsg main\nfrom=photofroggy\n\nStupid message here.')
        event = self.parser.mapper(packet)
        
        ''' Time to make sure we got the right data out of the protocol parser.
            The data returned should look like this:
                
                data = {
                    'event': 'recv_msg',
                    'args': {
                        'ns': 'chat:Botdom',
                        'user': 'photofroggy',
                        'message': 'Stupid message here.',
                        'raw': 'recv chat:Botdom\n\nmsg main\nfrom=photofroggy\n\nStupid message here.'
                    },
                    'rules': [
                        ('ns', 'chat:Botdom'),
                        ('user', 'photofroggy'),
                        ('message', 'Stupid message here.'),
                        ('raw', 'recv chat:Botdom\n\nmsg main\nfrom=photofroggy\n\nStupid message here.')
                    ]
                }
            
            There is always an entry in the 'args' dictionary for every tuple
            in 'rules', so for every tuple in 'rules', we know that the
            corresponding 'args' key-value pair exists. This could make testing
            easier, but it's trivial to test both.
        '''
        expected = [
            ('ns', 'chat:Botdom'),
            ('user', 'photofroggy'),
            ('message', 'Stupid message here.'),
            ('raw', 'recv chat:Botdom\n\nmsg main\nfrom=photofroggy\n\nStupid message here.')
        ]
        
        for rule in expected:
            try:
                arg = event.arg(rule[0])
                self.failIf(arg != rule[1],
                    'Protocol parser stored an incorrect {0} value in the event object'.format(rule[0]))
            except KeyError:
                self.fail('Protocol parser failed to store {0} value in the event object'.format(rule[0]))
    
    def test_message_generating(self):
        """ Test the ``logger`` method to make sure it generates messages properly. """
        packet = Packet('recv chat:Botdom\n\nmsg main\nfrom=photofroggy\n\nStupid message here.')
        data = self.parser.mapper(packet)
        
        log_list = self.parser.logger(data, '#Botdom', packet.raw)
        
        self.failIf(log_list is None,
            'Protocol parser did not recognise the given packet')
        
        self.failIf(log_list[0] != '<photofroggy> Stupid message here.',
            'The logger method did not render the correct log message')
        
        self.failIf(log_list[1] != '#Botdom',
            'The logger method returned with the wrong channel namespace')
        
        self.failIf(not log_list[2],
            'The logger method returned with the wrong value for `showns`')
        
        self.failIf(log_list[3],
            'The logger method returned with the wrong value for `mute`')
        
        self.failIf(log_list[4] != 'recv chat:Botdom\n\nmsg main\nfrom=photofroggy\n\nStupid message here.',
            'The logger method did not return the raw packet')


# EOF