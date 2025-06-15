import re
import sys
import os

class BasicInterpreter:
    def __init__(self):
        self.variables = {}
        self.lines = {}
        self.current_line = 0
        self.next_line = 0
        self.program_end = False
        self.classes = {}
        self.objects = {}
        self.current_class = None
        self.in_method = False
        self.method_body = []
        self.method_params = []

    def load_program(self, filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('!'):
                        continue
                    
                    # Обработка строк с номерами и без
                    if line[0].isdigit():
                        space_pos = line.find(' ')
                        line_num = int(line[:space_pos])
                        statement = line[space_pos+1:].strip()
                    else:
                        line_num = len(self.lines) * 10 + 10
                        statement = line
                    
                    self.lines[line_num] = statement
        except FileNotFoundError:
            print(f"File not found: {filename}")
            sys.exit(1)

    def run(self):
        self.next_line = min(self.lines.keys()) if self.lines else 0
        while not self.program_end and self.next_line is not None:
            self.current_line = self.next_line
            if self.current_line not in self.lines:
                self.next_line = self.get_next_line()
                continue
                
            statement = self.lines[self.current_line]
            self.execute_statement(statement)
            if self.next_line == self.current_line:
                self.next_line = self.get_next_line()

    def get_next_line(self):
        sorted_lines = sorted(self.lines.keys())
        for line in sorted_lines:
            if line > self.current_line:
                return line
        return None

    def execute_statement(self, statement):
        if self.in_method:
            if statement.upper().startswith('END METHOD'):
                self.classes[self.current_class]['methods'][self.current_method] = {
                    'body': self.method_body,
                    'params': self.method_params
                }
                self.in_method = False
            else:
                self.method_body.append(statement)
            return

        tokens = re.findall(r'"[^"]*"|\S+', statement)
        if not tokens:
            return

        keyword = tokens[0].upper()
        args = tokens[1:]

        try:
            if keyword == 'PRINT':
                self.execute_print(args)
            elif keyword == 'LET':
                self.execute_let(args)
            elif keyword == 'CLASS':
                self.execute_class(args)
            elif keyword == 'METHOD':
                self.execute_method(args)
            elif keyword == 'NEW':
                self.execute_new(args)
            elif keyword == 'CALL':
                self.execute_call(args)
            elif keyword == 'ENDCLASS':
                self.current_class = None
            elif '=' in statement:
                parts = statement.split('=', 1)
                var = parts[0].strip()
                expr = parts[1].strip()
                self.variables[var] = self.evaluate_expression(expr)
        except Exception as e:
            print(f"Error in line {self.current_line}: {str(e)}")

    def execute_print(self, args):
        output = []
        for arg in args:
            if arg.startswith('"') and arg.endswith('"'):
                output.append(arg[1:-1])
            else:
                value = self.evaluate_expression(arg)
                output.append(str(value))
        print(' '.join(output))

    def execute_let(self, args):
        if len(args) < 2 or args[1] != '=':
            raise ValueError("Invalid LET syntax")
        var = args[0]
        expr = ' '.join(args[2:])
        self.variables[var] = self.evaluate_expression(expr)

    def execute_class(self, args):
        if not args:
            raise ValueError("Class name required")
        self.current_class = args[0]
        self.classes[self.current_class] = {'methods': {}}

    def execute_method(self, args):
        if not self.current_class:
            raise ValueError("Method outside class")
        if not args:
            raise ValueError("Method name required")

        method_decl = ' '.join(args)
        match = re.match(r'(\w+)(?:\((.*)\))?', method_decl)
        if not match:
            raise ValueError("Invalid method syntax")

        self.current_method = match.group(1)
        self.method_params = [p.strip() for p in match.group(2).split(',')] if match.group(2) else []
        self.in_method = True
        self.method_body = []

    def execute_new(self, args):
        if len(args) < 2 or args[1] != '=':
            raise ValueError("Invalid NEW syntax")
        
        var_name = args[0]
        class_name = args[2]
        
        if class_name not in self.classes:
            raise ValueError(f"Class {class_name} not defined")
        
        obj_id = f"obj_{len(self.objects)}"
        self.objects[obj_id] = {'class': class_name, 'properties': {}}
        self.variables[var_name] = obj_id

        # Call init method if exists
        if 'init' in self.classes[class_name]['methods']:
            init_args = []
            if len(args) > 3:
                init_args = self.parse_args(' '.join(args[3:]))
            self.call_method(obj_id, 'init', init_args)

    def execute_call(self, args):
        if len(args) < 3 or args[1] != '.':
            raise ValueError("Invalid CALL syntax. Use: CALL object.method(arg1, arg2)")
        
        # Разбираем вызов метода: object.method(arg1, arg2)
        obj_name = args[0]
        method_part = args[2]
        
        # Отделяем имя метода от аргументов
        if '(' in method_part:
            method_name = method_part.split('(')[0]
            method_args_str = method_part.split('(')[1].rstrip(')')
            method_args = [arg.strip() for arg in method_args_str.split(',')] if method_args_str else []
        else:
            method_name = method_part
            method_args = []
        
        if obj_name not in self.variables:
            raise ValueError(f"Object {obj_name} not found")
        
        obj_id = self.variables[obj_name]
        self.call_method(obj_id, method_name, method_args)

        def call_method(self, obj_id, method_name, args):
            if obj_id not in self.objects:
                raise ValueError(f"Object {obj_id} not found")
            
            class_name = self.objects[obj_id]['class']
            if method_name not in self.classes[class_name]['methods']:
                raise ValueError(f"Method {method_name} not found in class {class_name}")
            
            method = self.classes[class_name]['methods'][method_name]
            
            # Save current state
            saved_vars = self.variables.copy()
            saved_lines = self.lines
            saved_line = self.current_line
            
            try:
                # Setup object context
                self.variables['this'] = obj_id
                self.variables.update(self.objects[obj_id]['properties'])
                
                # Set method parameters
                for param, arg in zip(method['params'], args):
                    self.variables[param] = self.evaluate_expression(arg)
                
                # Execute method body
                self.lines = {i*10+10: line for i, line in enumerate(method['body'])}
                self.current_line = 10
                self.next_line = 10
                self.program_end = False
                
                while not self.program_end and self.next_line is not None:
                    self.current_line = self.next_line
                    if self.current_line in self.lines:
                        self.execute_statement(self.lines[self.current_line])
                    self.next_line = self.get_next_line()
                
                # Save object properties
                for prop in self.objects[obj_id]['properties']:
                    if prop in self.variables:
                        self.objects[obj_id]['properties'][prop] = self.variables[prop]
                        
            finally:
                # Restore state
                self.variables = saved_vars
                self.lines = saved_lines
                self.current_line = saved_line

    def parse_args(self, arg_str):
        if arg_str.startswith('(') and arg_str.endswith(')'):
            return [a.strip() for a in arg_str[1:-1].split(',')]
        return []

    def evaluate_expression(self, expr):
        expr = expr.strip()
        
        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        # Boolean values
        if expr.upper() == 'TRUE':
            return True
        if expr.upper() == 'FALSE':
            return False
        
        # Variable
        if expr in self.variables:
            return self.variables[expr]
        
        # Numeric expression
        try:
            return eval(expr, {'__builtins__': None}, {})
        except:
            return expr

def main():
    if len(sys.argv) != 2:
        print("Usage: python basic.py program.bas")
        sys.exit(1)
    
    interpreter = BasicInterpreter()
    interpreter.load_program(sys.argv[1])
    interpreter.run()

if __name__ == "__main__":
    main()