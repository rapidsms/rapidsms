#!/usr/bin/env python
# vim: noet


def querydict_to_dict(qd):
	return dict((str(k), v) for k, v in qd.iteritems())


from django.db.models.fields import DateField

def from_querydict(model, qd, other=None, suffix=""):
	dict = querydict_to_dict(qd)
	obj_dict = {}
	
	# if applicable, merge the 'other' dict,
	# which contains pre-filled values, not
	# from a query dict
	if other is not None:
		for k, v in other.iteritems():
			dict[str(k) + suffix] = v
	
	# iterate the fields in the model, building
	# a dict of matching POSTed values as we go
	for field in model._meta.fields:
		fn = field.name
		fns = fn + suffix
		
		# if an exact match was
		# POSTed, then use that
		if fns in dict:
			obj_dict[fn] = dict[fns]
		
		# date fields can be provided as three
		# separate values, so D/M/Y <select>
		# elements can easily be used
		elif isinstance(field, DateField):
			try:
				obj_dict[fn] = "%4d-%02d-%02d" % (
					int(dict[fns+"-year"]),
					int(dict[fns+"-month"]),
					int(dict[fns+"-day"]))
			
			# choo choooo...
			# all aboard the fail train
			except KeyError:
				pass
	
	return obj_dict


# create an instance based upon the dict extracted by from_querydict
def insert_via_querydict(model, qd, other=None, suffix=""):
	return model(**from_querydict(model, qd, other, suffix))


# as above, but update an instance..
def update_via_querydict(instance, qd, other=None, suffix=""):
	for k,v in from_querydict(instance.__class__, qd, other, suffix).iteritems():
		setattr(instance, k, v)
	
	# send back the instance, so we can
	# chain a .save call on to the end
	return instance


def field_bundles(qd, *keys):
	"""When an HTML form has multiple fields with the same name, they are received
	   as a single key, with an array of values -- which looks something like:
	   
     { "backend": ["a", "b"], "identity": ["111", "222"], **other_stuff }
      
     ...which isn't very easy to iterate as pairs of "backend" and "identity";
     which is most often what we want to do. This method inverts the axis,
     and returns the same data in the less verbose, and more useful format:
     
     [("a", "111"), ("b", "222")]
     
     The order of tuples is preserved from the querydict - this USUALLY means
     that they'll be output in the same order as the controls on the HTML form
     that the request was triggered by - but that's not guaranteed. The order
     of the values inside the tuples (originally, the keys) is derrived from
     the *keys argument(s). Using the input from the first example, to output
     the second, in a familiar view:
     
     field_bundles(request.POST, "backend", "identity")"""
  
	bundles = []
	length = None
	
	# check that all values are of the same
	# length, even if that is zero, to avoid
	# creating half-bundles with missing data
	for key in keys:
		
		# if this is the first pair, then store the length
		# of the value, to check against subsequent pairs
		kl = len(qd.getlist(key))
		if length is None:
			length = kl
		
		# not the first pair, so we know long the value
		# SHOULD be - if it isn't exactly right, abort
		elif length != kl:
			raise IndexError(
				"for %s, expected length of %d, got %d" % (
					key, length, kl))
	
	# iterate all of the data that we're going to
	# capture, and invert the axis, to group bundles
	# togeter, rather than parameters
	for n in range(0, length):
		bundles.append([qd.getlist(k)[n] for k in keys])
	
	return bundles
