from models import *
from django.contrib.contenttypes.models import ContentType
from types import ListType,TupleType



def getImmediateRelationsForObject(content_obj):
    ctype = ContentType.objects.get_for_model(content_obj)
    cid = content_obj.id
    parent_edges = Edge.objects.all().filter(child_type=ctype,child_id=cid)
    child_edges = Edge.objects.all().filter(parent_type=ctype,parent_id=cid)    
    return (parent_edges, child_edges)
    


def getAncestorEdgesForObject(content_obj):
    #todo:  get all edges
    # for each edge, get full lineage
    #return multidimensional array
    #[[1,2,3],[[a,b,c],d,e,[f,g[h]]]
    ctype = ContentType.objects.get_for_model(content_obj)
    cid = content_obj.id
    parent_edges = Edge.objects.all().filter(child_type=ctype,child_id=cid)
    if len(parent_edges) == 0:
        return []
    else:
        ret = []        
        for edge in parent_edges:
            ret.append(edge)            
            parents = getAncestorEdgesForObject(edge.parent_object)                                 
            if len(parents) > 0:
                ret.append(parents)        
        return ret

def getDescendentEdgesForObject(content_obj):    
    ctype = ContentType.objects.get_for_model(content_obj)
    cid = content_obj.id
    child_edges = Edge.objects.all().filter(parent_type=ctype,parent_id=cid)
    
    if len(child_edges) == 0:
        return []
    else:
        ret = []
        for edge in child_edges:
            children = getDescendentEdgesForObject(edge.child_object)
            ret.append(edge)
            if len(children) > 0:
                ret.append(children)
        return ret



def getFamilyTreeForObject(content_obj):
    #todo:  get all edges
    # for each edge, get full lineage
    #return multidimensional array
    #[[1,2,3],[[a,b,c],d,e,[f,g[h]]]
    ctype = ContentType.objects.get_for_model(content_obj)
    cid = content_obj.id
    parent_edges = Edge.objects.all().filter(child_type=ctype,child_id=cid)
    
    if len(parent_edges) == 0:
        return [content_obj]
    else:
        ret = [content_obj]
        for edge in parent_edges:
            ret.append(getFamilyTreeForObject(edge.parent_object))
        return ret

def getFullDescendantsForObject(content_obj):
    #todo:  get all edges
    # for each edge, get full lineage
    #return multidimensional array
    #[[1,2,3],[[a,b,c],d,e,[f,g[h]]]
    ctype = ContentType.objects.get_for_model(content_obj)
    cid = content_obj.id
    child_edges = Edge.objects.all().filter(parent_type=ctype,parent_id=cid)
    
    if len(child_edges) == 0:
        return [content_obj]
    else:
        ret = [content_obj]
        for edge in child_edges:
            ret.append(getFullDescendantsForObject(edge.child_object))
        return ret

def getLinearAncestryForEdge(edge):
    #todo:
    #base case:  get content object, content id.
    #big assumption is that the edgetype will stay constant in this query
    parent_type = edge.relationship.parent_type
    parent_id = edge.parent_id
        
    #does this edge's parents have parents?
    grandparents = Edge.objects.all().filter(relationship=edge.relationship, child_type=parent_type, child_id=parent_id)
    #print len(grandparents)
    if len(grandparents) == 0:
        #no it does not, we're just going to return the parent object because this is the highest ancestor        
        return [edge.child_object,edge.parent_object]
    else:
        #yes it has a higher ancestor.  We will return the current child (that's what we're querying), and get the prior generation
        return [edge.child_object] + getLinearAncestryForEdge(grandparents[0])  
    #check edge table, if has no parent, return
    #return as list    