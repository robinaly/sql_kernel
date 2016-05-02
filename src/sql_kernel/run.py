import functools
import operator
import types
import csv
import six
import codecs
import os.path
import re
import sqlalchemy
import sqlparse
import prettytable


def unduplicate_field_names(field_names):
    """Append a number to duplicate field names to make them unique. """
    res = []
    for k in field_names:
        if k in res:
            i = 1
            while k + '_' + str(i) in res:
                i += 1
            k += '_' + str(i)
        res.append(k)
    return res

class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = six.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        if six.PY2:
            _row = [s.encode("utf-8")
                    if hasattr(s, "encode")
                    else s
                    for s in row]
        else:
            _row = row
        self.writer.writerow(_row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        if six.PY2:
           data = data.decode("utf-8")
           # ... and reencode it into the target encoding
           data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
        self.queue.seek(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def _nonbreaking_spaces(match_obj):
    """
    Make spaces visible in HTML by replacing all `` `` with ``&nbsp;``

    Call with a ``re`` match object.  Retain group 1, replace group 2
    with nonbreaking speaces.
    """
    spaces = '&nbsp;' * len(match_obj.group(2))
    return '%s%s' % (match_obj.group(1), spaces)

_cell_with_spaces_pattern = re.compile(r'(<td>)( {2,})')


class ResultSet(list):
    """
    Results of a SQL query.

    Can access rows listwise, or by string value of leftmost column.
    """
    def __init__(self, sqlaproxy, sql, config):
        self.keys = sqlaproxy.keys()
        self.sql = sql
        self.config = config
        self.limit = config.autolimit
        style_name = config.style
        self.style = prettytable.__dict__[style_name.upper()]
        self.returns_rows = sqlaproxy.returns_rows
        self.field_names = []
        self.rowcount = sqlaproxy.rowcount
        if sqlaproxy.returns_rows:
            if self.limit:
                list.__init__(self, sqlaproxy.fetchmany(size=self.limit))
            else:
                list.__init__(self, sqlaproxy.fetchall())
            self.field_names = unduplicate_field_names(self.keys)
            self.pretty = prettytable.PrettyTable(self.field_names)
            if not config.autopandas:
                for row in self[:config.displaylimit or None]:
                    self.pretty.add_row(row)
            self.pretty.set_style(self.style)
        else:
          
            list.__init__(self, [])
            self.pretty = None
            
    def _repr_html_(self):
        _cell_with_spaces_pattern = re.compile(r'(<td>)( {2,})')
        if self.pretty:
            result = self.pretty.get_html_string()
            result = _cell_with_spaces_pattern.sub(_nonbreaking_spaces, result)
            if self.config.displaylimit and len(self) > self.config.displaylimit:
              result = result + '\n<span>%d row(s), %d shown, %d column(s)</span>' % (
                    len(self), self.config.displaylimit, len(self.field_names))
            else:
              result = result + '\n<span>%d row(s), %d column(s)</span>' % (
                    len(self), len(self.field_names))
            return result
        else:
            if self.rowcount < 0:
              self.rowcount = 0
            return "<span>Done %d row(s) affected</span>" % self.rowcount
    
    def metadata(self):
      if self.pretty:
        return {'rowcount': len(self), 'columncount': len(self.field_names), 'columnnames': self.field_names}
      else:
        return {'rowcount': self.rowcount, 'columncount': 0, 'columnames': self.field_names}
            
    def __str__(self, *arg, **kwarg):
        return unicode(self.pretty or 'Done')
        
    def __getitem__(self, key):
        """
        Access by integer (row position within result set)
        or by string (value of leftmost column)
        """
        try:
            return list.__getitem__(self, key)
        except TypeError:
            result = [row for row in self if row[0] == key]
            if not result:
                raise KeyError(key)
            if len(result) > 1:
                raise KeyError('%d results for "%s"' % (len(result), key))
            return result[0]
            
    def dict(self):
        "Returns a dict built from the result set, with column names as keys"
        return dict(zip(self.keys, zip(*self)))

def run(conn, sql, config, user_namespace={}):
  rowcount = 0
  for statement in sqlparse.split(sql):
    txt = sqlalchemy.sql.text(statement)
    result = conn.session.execute(txt, user_namespace)

  resultset = ResultSet(result, statement, config)
    
  return resultset
