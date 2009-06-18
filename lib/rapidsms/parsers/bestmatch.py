#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from __future__ import with_statement
import re
import threading
import sys

class BestMatch():
    targets=set()
    prefix_map={}
    lock=threading.Lock()
    pp_targets=None # 'pre-processed' targets
    target_data=dict()

    def __init__(self, targets=None, ignore_prefixes=None):
        self.set_targets(targets)
        self.set_ignore_prefixes(ignore_prefixes)
    
    def match(self,src,anchored=True,with_data=False):
        """
        Returns a sequence of matched targets.
        The sequence may of 0,1, or more matches
        
        anchored -- means anchor source string at beginning of line.
                    E.g. matching 'foo' against 'baz bar foo' with not match
                    anchored, but will unanchored.

        with_data -- when True, return a list of tuples of 
                     (matched target, stored target data)

        """
        results=set()

        # short circuit do-nothing case
        if src is None or self.targets is None or len(self.targets)==0:
            return results

        src=src.strip()

        if len(src)==0:
            return results

        # lock everything so targets can't change underneath us
        with self.lock:
            # make sure targets are processed
            self.__process_targets()

        if anchored:
            anchor=ur'^'
        else:
            anchor=ur'.*'

        src_stripped=dict()
        # match against the prefixes to see if we can cut it down
        for p,rx in self.prefix_map.items():
            pre_m=rx.match(src)
            if pre_m is not None:
                stripped=pre_m.groups()[0]
                src_stripped[p]=re.compile(ur'%s%s.*' % \
                                          (anchor, re.escape(stripped)), \
                                          re.IGNORECASE)
                # now see if me can match under that prefix
                for target,to_match in self.pp_targets[p]:
                    if src_stripped[p].match(to_match) is not None:
                        results.add(target)

        # if we couldn't strip down by prefix, check full
        # source against all targets
        src_matcher=re.compile(ur'%s%s.*' % \
                                   (anchor, re.escape(src)), \
                                   re.IGNORECASE)
        for pre in self.pp_targets.keys():
            for target,to_match in self.pp_targets[pre]:
                if src_matcher.match(to_match) is not None:
                    results.add(target)
        
        if with_data:
            data_results=list()
            for t in results:
                data=None
                if t in self.target_data:
                    data=self.target_data[t]
                    data_results.append((t,data))
            return data_results
        else:
            return list(results)

    def __process_targets(self):
        # only need to if pp_targets is None
        # and we have some targets!
        if len(self.targets)==0 or \
                self.pp_targets is not None:
            return 

        # strip targets of prefixes
        # NOTE: Each target gets stripped of prefix only ONCE
        # SO if you have targets that may have
        # multiple prefixes 'Mr. Doctor. Smith', you need to add compound
        # prefixes like ['Mr.','Dr.','Mr. Doctor.']
        self.pp_targets=dict()
        for t in self.targets:
            # try to match a prefix
            for p,rx in self.prefix_map.items():
                if not p in self.pp_targets:
                    self.pp_targets[p]=set()
                m = rx.match(t)
                if m is not None:
                    left_over=m.groups()[0]
                    self.pp_targets[p].add((t,left_over))
            # now add actual string
            if '' not in self.pp_targets:
                self.pp_targets['']=set()
            self.pp_targets[''].add((t,t))

        return self.pp_targets

    def __reset_prepped_targets(self):
        self.pp_targets=None

    #
    # A slew of convenient setters/getters
    #
    def get_targets(self):
        """Returns match targets as a set"""
        return self.targets

    def set_targets(self,val):
        if val is None or len(val)==0:
            self.targets=set()
        else:
            for v in val:
                self.add_target(v)
        
        self.__reset_prepped_targets()
    
    def get_ignore_prefixes(self):
        """Return ignore prefixes as a set"""
        with self.lock:
            pres=self.prefix_map.keys()
        return pres

    def set_ignore_prefixes(self,val):
        """Takes a sequence of prefix strings"""
        # case of full remove
        if val is None or len(val)==0: 
            with self.lock:
                self.prefix_map=dict()
                return

        for v in val:
            self.add_ignore_prefix(v)


    def add_target(self,val):
        # standard empty cases... should be a method on string...
        if val is None: return

        # check for something that we interpet as (target,data)
        target=val
        data=None
        if isinstance(val, tuple):
            target,data=val

        target=target.strip()
        if len(target)==0: return

        with self.lock:
            self.targets.add(target)
            self.target_data[target]=data

        self.__reset_prepped_targets()

    def add_ignore_prefix(self,val):
        with self.lock:
            if val in self.prefix_map: return
            self.prefix_map[val]=\
                re.compile(ur'^%s\s*(.*)' % re.escape(val),\
                               re.IGNORECASE)
        self.__reset_prepped_targets()

    def remove_target(self,val):
        """Returns 'True' if removed, 'False' if not in the set"""
        with self.lock:
            try:
                targets.remove(val)
            except KeyError:
                return False
            
        self.__reset_prepped_targets()
        return True

    def remove_ignore_prefix(self,val):
        """Returns 'True' if removed, 'False' if not in the set"""
        with self.lock:
            try:
                del self.prefix_map[val]
            except KeyError:
                return False
        
        self.__reset_prepped_targets()
        return True


# cruddy manual test script

if __name__ == "__main__":
    src='mr'

    if len(sys.argv)>1:
        targ=sys.argv[1]

    src=sys.argv[1]

    targets=['jeff','john','jimmy','mary','mr. smith','mr. smuthers','mrs. smith',('mr. smith-edwards*','foo'),'mr. jones']
#    targets=['mr. smith', 'mr. jones']
    bm=BestMatch(targets,['mr.','mrs.'])
    print "found: %s" %  bm.match(src,with_data=True)
