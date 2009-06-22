#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

import unittest
from bestmatch import BestMatch

command_targets = [
    'join','leave','name','create'
]

command_data = [
    lambda:'join_data', 'leave_data',None,{'key':'value'}
]

city_targets = [
    'newton','westfield','springfield','newberry','new orleans','san fransico',
    'san diego', 'santo domingo', 'san jose'
]

resto_targets=[
    'chez panisse','chez lando','chez raoul','casa guadalupe','casa de fruta','hotel utah',
    'hotel lando','hotel chez lando','burger king','burgerville','burger heaven'
]

similar_targets=[
    'fred','freddy','fredalicious','bob','bobby','barry','bo'
]

class TestBestMatch(unittest.TestCase):
    
    def setUp(self):
        self.cityM=BestMatch(city_targets)
        self.cmdM=BestMatch(command_targets)    
        self.restoM=BestMatch(resto_targets)    
        self.simiM=BestMatch(similar_targets)

    def testExactMatch(self):
        print "EXACT MATCHING"
        print "Find 'bob'"
        res=self.simiM.match('bob')
        self.assertTrue(len(res)==1 and res[0]=='bob')

    def testBasicMatch(self):
        print "BASIC MATCHING"
        print "Find 'join'"
        res=self.cmdM.match('join')
        self.assertTrue(len(res)==1 and res[0]=='join')

        print "Find 'j'"
        res=self.cmdM.match('j')
        self.assertTrue(len(res)==1 and res[0]=='join')

        print "Find None"
        res=self.cmdM.match(None)
        self.assertTrue(len(res)==0)

        print "Find ''"
        res=self.cmdM.match('')
        self.assertTrue(len(res)==0)

        print "Add and find 'help'"
        self.cmdM.add_target('help')
        res=self.cmdM.match('help')
        self.assertTrue(len(res)==1 and res[0]=='help')

        print "Still find 'join'"
        res=self.cmdM.match('j')
        self.assertTrue(len(res)==1 and res[0]=='join')

        print "Add 'later' and find 'later'"
        self.cmdM.add_target('later')
        res=self.cmdM.match('later')
        self.assertTrue(len(res)==1 and res[0]=='later')

        print "Find 'l' and get 'later' and 'leave'"
        res=self.cmdM.match('l')
        self.assertTrue(set(res)==set(['later','leave']))

    def testUnAnchored(self):
        print "UNANCHORED SEARCH"
        res=self.cityM.match('field',anchored=False)
        print "Unanchored search for 'field': %s" % ','.join(res)
        self.assertTrue(set(res)==set(['springfield','westfield']))

    def testPrefixMatch(self):
        print "IGNORE PREFIX MATCHING"
        res=self.restoM.match('panisse',anchored=True)
        print "Unprefixed search for 'panisse': %s" % ','.join(res)
        self.assertTrue(len(res)==0)

        print "Add prefix 'chez'"
        self.restoM.add_ignore_prefix('chez')
        res=self.restoM.match('panisse',anchored=True)
        print "Prefixed search for 'panisse': %s" % ','.join(res)
        self.assertTrue(len(res)==1 and res[0]=='chez panisse')

        res=self.restoM.match('chez',anchored=True)
        print "Prefixed search for 'chez': %s" % ','.join(res)
        self.assertTrue(set(res)==set(resto_targets[:3]))

        print "Add 'hotel' to prefix list"
        self.restoM.add_ignore_prefix('hotel')
        res=self.restoM.match('lando',anchored=True)
        print "Prefixed search for 'lando': %s" % ','.join(res)
        self.assertTrue(set(res)==set(['chez lando','hotel lando']))

        print "Add 'burger' to prefix list"
        self.restoM.add_ignore_prefix('burger')
        res=self.restoM.match('burger',anchored=True)
        print "Prefixed search for 'burger': %s" % ','.join(res)
        self.assertTrue(set(res)==set(resto_targets[-3:]))

    def testWithData(self):
        print "TARGETS WITH DATA"
        self.cmdM.set_targets(zip(command_targets,command_data))

        print "Retrieve function for data"
        res=self.cmdM.match('j',with_data=True)
        self.assertTrue(res[0][1]()=='join_data')

        print "Retrieve string"
        res=self.cmdM.match('le',with_data=True)
        self.assertTrue(res[0][1]=='leave_data')

        print "Retrieve None"
        res=self.cmdM.match('n',with_data=True)
        self.assertTrue(res[0][1] is None)

        print "Retrieve dict"
        res=self.cmdM.match('cr',with_data=True)
        self.assertTrue(res[0][1]['key']=='value')

if __name__ == '__main__':
    unittest.main()
