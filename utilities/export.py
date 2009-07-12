import csv
from django.template.defaultfilters import slugify
from django.http import HttpResponse

def export(qs, fields=None, format='csv'):
    model = qs.model
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
    writer = csv.writer(response)
    # Write headers to CSV file
    if fields:
        headers = fields
    else:
        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
    writer.writerow(headers)
    # Write data to CSV file
    for obj in qs:
        row = []
        for field in headers:
            if field in headers:
                val = getattr(obj, field)
                if callable(val):
                    val = val()
                if hasattr(obj, "get_" + field + "_display"):
                    val2 = getattr(obj, "get_" + field + "_display")
                    if callable(val2):
                        val = val2()
                row.append(val)
        writer.writerow(row)
    # Return CSV file to browser as download
    return response