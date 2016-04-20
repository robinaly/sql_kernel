from ipykernel.kernelbase import Kernel

from sqlalchemy.exc import ProgrammingError, OperationalError

import connection
import run

try:
  from traitlets.config.configurable import Configurable
  from traitlets import Bool, Int, Unicode
except ImportError,e:
  from IPython.config.configurable import Configurable
  from IPython.utils.traitlets import Bool, Int, Unicode

__version__ = '0.1'

def parse(cell, config):
  '''
  Parse Command
  '''
  parts = [part.strip() for part in cell.split(None, 1)]
  if not parts:
      return {'op': 'NOP', 'statement': ''}
  if '@' in parts[0] or '://' in parts[0]:
    connection = parts[0]
    return {'op': 'CONNECT', 'statement': connection.strip()}
  else:
    return {'op': 'SQL', 'statement': cell.strip()}

class SqlKernel(Kernel):
    implementation = 'ipython'
    implementation_version = __version__

    @property
    def language_version(self):
      return __version__

    @property
    def banner(self):
      return self.implementation + " " + __version__

    language_info = {'name': 'sql',
                     'mimetype': 'text/x-sql',
                     'codemirror_mode': 'sql',
                     'file_extension': '.sql'}

    autolimit = Int(0, config=True, help="Automatically limit the size of the returned result sets")
    style = Unicode('DEFAULT', config=True, help="Set the table printing style to any of prettytable's defined styles (currently DEFAULT, MSWORD_FRIENDLY, PLAIN_COLUMNS, RANDOM)")
    short_errors = Bool(True, config=True, help="Don't display the full traceback on SQL Programming Error")
    displaylimit = Int(0, config=True, help="Automatically limit the number of rows displayed (full result set is still stored)")
    autopandas = Bool(False, config=True, help="Return Pandas DataFrames instead of regular result sets")
    column_local_vars = Bool(False, config=True, help="Return data into local variables from column names")
    feedback = Bool(False, config=True, help="Print number of rows affected by DML")

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self.conn = None
        
        for code in ['sqlite://']:
          connection.Connection.get(code)

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
      '''
      Main method executing code
      '''
      cmd = parse(code, self)
      if cmd['op'] == 'NOP': # empty line
        pass
      elif cmd['op'] == 'CONNECT': # connection statement
        try:
          connection.Connection.get(cmd['statement'])
        
          data = { 
                   'text/plain': "Connected", 
                 }
          stream_content = {'execution_count': self.execution_count, 'data': data, 'metadata': {} }
          self.send_response(self.iopub_socket, 'execute_result', stream_content)
          return {'status': 'ok',
                  'execution_count': self.execution_count,
                  'payload': [],
                  'user_expressions': {},
                 }
        except:
          stream_content = {'name': 'stderr', 'text': "Errror connecting" }
          self.send_response(self.iopub_socket, 'stream', stream_content)
          return {'status': 'failure',
                  'execution_count': self.execution_count,
                  'payload': [],
                  'user_expressions': {},
                 }
      elif cmd['op'] == 'SQL': # SQL Statement(s)
        if connection.Connection.current == None:
          # not yet connected
          stream_content = {'name': 'stderr', 'text': "Not connected yet" }
          self.send_response(self.iopub_socket, 'stream', stream_content)
          return {'status': 'failure',
                  'execution_count': self.execution_count,
                  'payload': [],
                  'user_expressions': {},
                 }
        try:
          result = run.run(connection.Connection.current, cmd['statement'], self, {})

          if not silent and result:
            data = { 
                     'text/plain': unicode(result), 
                     'text/html': result._repr_html_() 
                   }
            stream_content = {'execution_count': self.execution_count, 'data': data, 'metadata': {} }
            self.send_response(self.iopub_socket, 'execute_result', stream_content)
          
          return {'status': 'ok',
                  'execution_count': self.execution_count,
                  'payload': [],
                  'user_expressions': {},
                 }
            
        except (Exception, ProgrammingError, OperationalError) as e:
          err_txt = str(e)
          remove_txt = '(sqlite3.OperationalError) '
          if err_txt.startswith(remove_txt):
            err_txt = err_txt[len(remove_txt):]
          stream_content = {'name': 'stderr', 'text': err_txt }
          self.send_response(self.iopub_socket, 'stream', stream_content)
      
          return {'status': 'failure',
                  'execution_count': self.execution_count,
                  'payload': [],
                  'user_expressions': {},
                 }
      else:
        print "Unknwon", cmd
        return {'status': 'failure',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }
             
    def do_shutdown(self, restart):
      pass
