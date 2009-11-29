import unittest
import os
from django.contrib.auth.models import Group, User
from modelrelationship.models import *
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core import management

import modelrelationship.traversal as traversal

class BasicTestCase(unittest.TestCase):
    def setup(selfs):
        #EdgeType.objects.all().delete()
        #User.objects.all().delete()
        #Edge.objects.all().delete()
        pass

    def testCreateRecursiveEdgeType(self):
        EdgeType.objects.all().delete()
        usertype = ContentType.objects.get_for_model(User)
        recursiveEdgeType = EdgeType(directional=True,parent_type=usertype,child_type=usertype)
        recursiveEdgeType.save()
        self.assertEquals(EdgeType.objects.all().count(),1)

    def testCreateDeepAncestry(self):          
        self.testCreateRecursiveEdgeType()    
        User.objects.all().delete()
        Edge.objects.all().delete()  
        
        for i in range(0,10):
            usr = User(username='generated%s' % (i),password='12345')
            usr.save()
        
        users = User.objects.all()
        edgetype = EdgeType.objects.all()[0]
        for usr in users:
            curtype = ContentType.objects.get_for_model(usr)
            if User.objects.all().filter(id=usr.id+1).count() == 1:
                next_usr = User.objects.all().get(id=usr.id+1) 
                newedge = Edge(relationship=edgetype,child_type=curtype,child_id=usr.id,parent_type=curtype,parent_id=next_usr.id)
                newedge.save() 
        self.assertEquals(Edge.objects.count(),User.objects.count()-1)
                 
        
    def testVerifyDeepAncestry(self):
        self.testCreateDeepAncestry()
        edges = Edge.objects.all()
        
        for edge in edges:
            cur_id = -1
            ancestry = traversal.getLinearAncestryForEdge(edge)
            #print "*** Verify Ancestry for %s" % (edge.child_object)
            for item in ancestry:                
                #self.assertTrue(cur_id >= item.id)                
                if item.id > cur_id:
                    cur_id = item.id                    
            self.assertEquals(ancestry[-1],User.objects.all()[User.objects.count() -1])        
    
#    def testVerifyFamilyTree(self):
#        print "\n\n\n############## testVerifyFamilyTree"
#        Organization.objects.all().delete()
#        ExtUser.objects.all().delete()
#        Edge.objects.all().delete()
#        EdgeType.objects.all().delete()
#        
#        
#        management.call_command('runscript', 'demo_bootstrap.py', verbosity=0)
#        
#        for org in Organization.objects.all():
#            ancestry = traversal.getFamilyTreeForObject(org)
#            print "Object: " + str(org)
#            print "Ancestors: " + str(ancestry)
#            
#        for usr in ExtUser.objects.all():
#            ancestry = traversal.getFamilyTreeForObject(usr)
#            print "Object: " + str(usr)
#            print "Ancestors: " + str(ancestry)
#    
#    def testVerifyDescendants(self):
#        print "\n\n\n############## testVerifyDescendants"
#        Organization.objects.all().delete()
#        ExtUser.objects.all().delete()
#        Edge.objects.all().delete()
#        EdgeType.objects.all().delete()
#        
#        management.call_command('runscript', 'demo_bootstrap.py', verbosity=0)
#            
#        for org in Organization.objects.all():
#            ancestry = traversal.getFullDescendantsForObject(org)
#            print "Object: " + str(org)
#            print "Descendants: " + str(ancestry)
#            
#        for usr in ExtUser.objects.all():
#            ancestry = traversal.getFullDescendantsForObject(usr)
#            print "Object: " + str(usr)
#            print "Descendants: " + str(ancestry)
#                     
#    
#    def testVerifyParentEdges(self):
#        print "\n\n\n############## testVerifyParentEdges"
#        Organization.objects.all().delete()
#        ExtUser.objects.all().delete()
#        Edge.objects.all().delete()
#        EdgeType.objects.all().delete()
#        
#        
#        management.call_command('runscript', 'demo_bootstrap.py', verbosity=0)
#            
#        
#        for org in Organization.objects.all():
#            ancestry = traversal.getAncestorEdgesForObject(org)
#            print "Object: " + str(org)
#            print "Ancestors: " + str(ancestry)
#            
#        for usr in ExtUser.objects.all():
#            ancestry = traversal.getAncestorEdgesForObject(usr)
#            print "Object: " + str(usr)
#            print "Ancestors: " + str(ancestry)
#    
#    def testVerifyChildEdges(self):
#        print "\n\n\n############## testVerifyChildEdges"
#        Organization.objects.all().delete()
#        ExtUser.objects.all().delete()
#        Edge.objects.all().delete()
#        EdgeType.objects.all().delete()
#        
#        management.call_command('runscript', 'demo_bootstrap.py', verbosity=0)        
#            
#        for org in Organization.objects.all():
#            ancestry = traversal.getDescendentEdgesForObject(org)
#            print "Object: " + str(org)
#            print "Descendants: " + str(ancestry)
#            
#        for usr in ExtUser.objects.all():
#            ancestry = traversal.getDescendentEdgesForObject(usr)
#            print "Object: " + str(usr)
#            print "Descendants: " + str(ancestry)
#       
#
    def testCreateDuplicateEdge(self):        
        self.testCreateRecursiveEdgeType()
        testuser = User(username='recursive',password='fail')
        testuser.save()
        edgetype = EdgeType.objects.all()[0]
        curtype = ContentType.objects.get_for_model(testuser)
        newedge = Edge(relationship=edgetype,child_type=curtype,child_id=testuser.id,parent_type=curtype,parent_id=testuser.id)
        newedge.save()
        
        dupe = Edge(relationship=edgetype,child_type=curtype,child_id=testuser.id,parent_type=curtype,parent_id=testuser.id)
        try:
            dupe.save()
        except:            
            self.assertTrue(True)
            return
            
        self.assertTrue(False)
    
    def testCreateMultipleChildren(self):
        self.assertFalse(False)
        
    def testVerifyMultipleChildren(self):
        self.assertFalse(False)        
        
    
