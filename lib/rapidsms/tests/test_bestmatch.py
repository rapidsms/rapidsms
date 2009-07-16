#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from rapidsms.parsers.bestmatch import BestMatch

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
        
    def test01BasicMatch(self):
        print
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

    def test02ExactMatch(self):
        print
        print "EXACT MATCHING"
        print "Find 'bob'"
        res=self.simiM.match('bob')
        print res
        self.assertTrue(len(res)==1 and res[0]=='bob')

    def test03UnAnchored(self):
        print
        print "UNANCHORED SEARCH"
        res=self.cityM.match('field',anchored=False)
        print "Unanchored search for 'field': %s" % ','.join(res)
        self.assertTrue(set(res)==set(['springfield','westfield']))

    def test04PrefixMatch(self):
        print
        print "IGNORE PREFIX MATCHING"
        res=self.restoM.match('panisse',anchored=True)
        print "Unprefixed search for 'panisse': %s" % ','.join(res)
        self.assertTrue(len(res)==0)

        print "Add prefix 'chez'"
        self.restoM.add_ignore_prefix('Chez')

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

    def test05WithData(self):
        print
        print "TARGETS WITH DATA"
        self.cmdM.targets=zip(command_targets,command_data)

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

    def test06AddRemoveTargets(self):
        print
        print 'Add Buffalo'
        self.cityM.add_target('buffalo')
        res = self.cityM.match('buf')
        self.assertTrue(len(res)==1 and res[0]=='buffalo')

        res = self.cityM.match('new')
        self.assertTrue(set(res)==set(['newton','newberry','new orleans']))

        print 'Remove Buffalo'
        self.cityM.remove_target('buffalo')
        res = self.cityM.match('buF')
        self.assertTrue(len(res)==0)

        print "Add prefix 'new'"
        self.cityM.add_ignore_prefix('new')
        res = self.cityM.match('ton')
        self.assertTrue(len(res)==1 and res[0]=='newton')

        print "Remove prefix 'new'"
        self.cityM.remove_ignore_prefix('new')
        res = self.cityM.match('ton')
        self.assertTrue(len(res)==0)

        print "Add target with data. (buffalo, rocks)"
        self.cityM.add_target(('buffalo','rocks'))
        res = self.cityM.match('BuF',with_data=True)
        self.assertTrue(len(res)==1 and res[0]==('buffalo','rocks'))

    def test07Aliases(self):
        print
        print "Add 'boston' with aliases 'the hub', 'beantown'"
        self.cityM.add_target(['boston', 'the hub', 'beantown'])
        print "Search for Beantown"
        res = self.cityM.match('beanTown')
        print res
        self.assertTrue(len(res)==1 and res[0]=='boston')
        
        print "Search for Boston"
        res = self.cityM.match('boston')
        self.assertTrue(len(res)==1 and res[0]=='boston')

        print "Add 'redsox country' as alias"
        self.cityM.add_alias_for_target('boston', 'redsox country')
        res = self.cityM.match('redsox')
        self.assertTrue(len(res)==1 and res[0]=='boston')

        print "Remove 'beantown'"
        self.cityM.remove_alias_for_target('boston', 'beantown')
        res = self.cityM.match('beantown')
        self.assertTrue(len(res)==0)

        print "Test get aliases"
        self.assertTrue(set(self.cityM.get_aliases_for_target('boston'))==
                        set(['redsox country', 'the hub']))

if __name__ == '__main__':
    unittest.main()
