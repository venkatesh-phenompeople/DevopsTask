from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from scipy.constants import convert_temperature
import numpy
import math
app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}

def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))

parser = reqparse.RequestParser()
parser.add_argument('task')
parser.add_argument('InputNumericalValue')
parser.add_argument('InputUnitofMeasure')
parser.add_argument('TargetUnitofMeasure')
parser.add_argument('StudentResponse')

# Todo
#   show a single todo item and lets you delete them
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        if (TODOS[todo_id]['InputUnitofMeasure'] not in ('Fahrenheit','Rankine','Kelvin','Celsius') or TODOS[todo_id]['TargetUnitofMeasure'] not in ('Fahrenheit','Rankine','Kelvin','Celsius')):
            result = {'result':'invalid','InputUnitofMeasure':TODOS[todo_id]['InputUnitofMeasure'],'TargetUnitofMeasure':TODOS[todo_id]['TargetUnitofMeasure']}
            return result
        elif (TODOS[todo_id]['StudentResponse'].isnumeric() or TODOS[todo_id]['StudentResponse'].split('.').last.size > 2):
            result = {'result':'incorrect','StudentResponse':TODOS[todo_id]['StudentResponse'], 'StudentResponseFloatSize':TODOS[todo_id]['StudentResponse'].split('.').last.size}
            return result


        result = {'result':'correct'}
        student_num  = numpy.fromstring(TODOS[todo_id]['StudentResponse'], dtype=int, sep=' ' )
        input_num =  numpy.fromstring(TODOS[todo_id]['InputNumericalValue'], dtype=int, sep=' ' )
        output_num = convert_temperature(input_num,TODOS[todo_id]['InputUnitofMeasure'].lower(),TODOS[todo_id]['TargetUnitofMeasure'].lower())
        if math.floor(student_num) == math.floor(output_num):
            result = {'result':'correct','StudentInput': numpy.array_str(student_num), 'ScientificOutput': numpy.array_str(output_num)}
            return result
        else:
            print(output_num,flush=True)
            result = {'result':'wrong','StudentInput': numpy.array_str(student_num), 'ScientificOutput': numpy.array_str(output_num)}
            return result
        # if TODOS[todo_id]['InputUnitofMeasure'] == 'Fahrenheit' and TODOS[todo_id]['TargetUnitofMeasure'] == 'Celsius':
        #     ft = TODOS[todo_id]['InputNumericalValue']
        #     ct = (ft -32) * 5 / 9.0
        #     if TODOS[todo_id]['StudentResponse'] == ct:
        #         result = {'result':'correct'}
        #     else:
        #         result = {'result':'wrong'}
        #     TODOS[todo_id].update(result)
        # return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task'],'InputNumericalValue': args['InputNumericalValue'],'InputUnitofMeasure': args['InputUnitofMeasure'],'TargetUnitofMeasure': args['TargetUnitofMeasure'],'StudentResponse': args['StudentResponse']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = 'todo%d' % (len(TODOS) + 1)
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')


if __name__ == '__main__':
    app.run(debug=True)
