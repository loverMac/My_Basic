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
        self.stack = []
        self.loops = []
        self.data = []
        self.data_ptr = 0

    def load_program(self, filename):
        try:
            filename = filename.replace('~', os.path.expanduser('~'))
            with open(filename, 'r', encoding='utf-8') as file:
                line_counter = 0
                for line in file:
                    line = line.split('!')[0].strip()
                    if not line:
                        continue
                    
                    match = re.match(r'^(\d+)\s+(.*)$', line)
                    if match:
                        line_num = int(match.group(1))
                        statement = match.group(2).strip()
                    else:
                        line_counter += 10
                        line_num = line_counter
                        statement = line.strip()
                    
                    self.lines[line_num] = statement
        except FileNotFoundError:
            print(f"Файл не найден: {filename}")
            sys.exit(1)
        except UnicodeDecodeError:
            print(f"Ошибка кодировки в файле: {filename}")
            sys.exit(1)

    def run(self):
        self.program_end = False
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
        lines = sorted(self.lines.keys())
        for i, line in enumerate(lines):
            if line > self.current_line:
                return line
        return None

    def execute_statement(self, statement):
        tokens = []
        in_quotes = False
        current_token = ""
        
        for char in statement:
            if char == '"':
                if in_quotes:
                    current_token += char
                    tokens.append(current_token)
                    current_token = ""
                    in_quotes = False
                else:
                    if current_token:
                        tokens.append(current_token)
                    current_token = char
                    in_quotes = True
            elif char.isspace() and not in_quotes:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char
        
        if current_token:
            tokens.append(current_token)

        if not tokens:
            return
            
        keyword = tokens[0].upper()
        
        try:
            if keyword == 'PRINT':
                self.execute_print(tokens[1:])
            elif keyword == 'LET':
                self.execute_let(tokens[1:])
            elif keyword == 'GOTO':
                self.execute_goto(tokens[1:])
            elif keyword == 'IF':
                self.execute_if(tokens[1:])
            elif keyword == 'FOR':
                self.execute_for(tokens[1:])
            elif keyword == 'NEXT':
                self.execute_next(tokens[1:])
            elif keyword == 'INPUT':
                self.execute_input(tokens[1:])
            elif keyword == 'END':
                self.program_end = True
            elif keyword == 'REM':
                pass
            elif keyword == 'DATA':
                self.execute_data(tokens[1:])
            elif keyword == 'READ':
                self.execute_read(tokens[1:])
            elif keyword == 'RESTORE':
                self.data_ptr = 0
            else:
                if '=' in statement:
                    parts = statement.split('=', 1)
                    var = parts[0].strip()
                    expr = parts[1].strip()
                    self.variables[var] = self.evaluate_expression(expr)
        except Exception as e:
            print(f"Ошибка в строке {self.current_line}: {str(e)}")

    def execute_print(self, args):
        output = []
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg == ';':
                pass
            elif arg == ',':
                output.append('\t')
            elif arg.startswith('"') and arg.endswith('"'):
                output.append(arg[1:-1])
            elif arg in ['+', '-', '*', '/', '=', '<>', '<=', '>=', '<', '>']:
                output.append(arg)
            else:
                try:
                    value = self.evaluate_expression(arg)
                    output.append(str(value))
                except:
                    output.append(arg)
            i += 1
        
        print(''.join(output))

    def execute_let(self, args):
        if len(args) < 2 or args[1] != '=':
            raise ValueError("Неверный синтаксис LET")
        
        var = args[0]
        expr = ' '.join(args[2:])
        self.variables[var] = self.evaluate_expression(expr)

    def execute_goto(self, args):
        if not args:
            raise ValueError("Требуется номер строки для GOTO")
        
        line_num = int(self.evaluate_expression(args[0]))
        if line_num not in self.lines:
            raise ValueError(f"Строка {line_num} не существует")
        
        self.next_line = line_num

    def execute_if(self, args):
        then_pos = -1
        for i, token in enumerate(args):
            if token.upper() == 'THEN':
                then_pos = i
                break
        
        if then_pos == -1:
            raise ValueError("Требуется THEN в операторе IF")
        
        condition = ' '.join(args[:then_pos])
        then_part = args[then_pos+1:]
        
        if self.evaluate_condition(condition):
            if then_part and then_part[0].isdigit():
                self.next_line = int(then_part[0])
            else:
                self.execute_statement(' '.join(then_part))

    def execute_for(self, args):
        if len(args) < 5 or args[1] != '=' or args[3].upper() != 'TO':
            raise ValueError("Неверный синтаксис FOR")
        
        var = args[0]
        start = int(self.evaluate_expression(args[2]))
        end = int(self.evaluate_expression(args[4]))
        
        step = 1
        if len(args) > 5 and args[5].upper() == 'STEP':
            step = int(self.evaluate_expression(args[6]))
        
        self.variables[var] = start
        self.loops.append({
            'var': var,
            'start': start,
            'end': end,
            'step': step,
            'loop_line': self.current_line,
            'next_line': self.get_next_line()
        })

    def execute_next(self, args):
        if not self.loops:
            raise ValueError("NEXT без FOR")
        
        loop = self.loops[-1]
        var = loop['var']
        
        if args and args[0] != var:
            raise ValueError(f"Ожидается NEXT {var}")
        
        self.variables[var] += loop['step']
        
        if (loop['step'] > 0 and self.variables[var] <= loop['end']) or \
           (loop['step'] < 0 and self.variables[var] >= loop['end']):
            self.next_line = loop['loop_line']
        else:
            self.loops.pop()

    def execute_input(self, args):
        if not args:
            raise ValueError("Требуется переменная для INPUT")
        
        prompt = "? "
        if args[0].startswith('"'):
            prompt = args[0][1:-1] + " "
            args = args[1:]
        
        for var in args:
            if var.endswith(','):
                var = var[:-1]
            
            while True:
                try:
                    value = input(prompt)
                    if value.upper() in ['TRUE', 'FALSE']:
                        self.variables[var] = value.upper() == 'TRUE'
                    else:
                        self.variables[var] = float(value) if '.' in value else int(value)
                    break
                except ValueError:
                    print("Неверный ввод. Попробуйте снова.")
                prompt = "?? "

    def execute_data(self, args):
        self.data.extend([d.strip() for d in ' '.join(args).split(',')])

    def execute_read(self, args):
        for var in args:
            if var.endswith(','):
                var = var[:-1]
            
            if self.data_ptr >= len(self.data):
                raise ValueError("Нет данных для чтения")
            
            value = self.data[self.data_ptr]
            try:
                if value.upper() in ['TRUE', 'FALSE']:
                    self.variables[var] = value.upper() == 'TRUE'
                else:
                    self.variables[var] = float(value) if '.' in value else int(value)
            except ValueError:
                self.variables[var] = value.strip('"')
            
            self.data_ptr += 1

    def evaluate_expression(self, expr):
        expr = expr.strip()
        
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        if expr.upper() == 'TRUE':
            return True
        if expr.upper() == 'FALSE':
            return False
        
        if expr in self.variables:
            return self.variables[expr]
        
        try:
            allowed_chars = set('0123456789+-*/(). ')
            if all(c in allowed_chars for c in expr):
                return eval(expr, {'__builtins__': None}, {})
            else:
                return expr
        except:
            return expr

    def evaluate_condition(self, condition):
        operators = ['=', '<>', '<=', '>=', '<', '>']
        
        for op in operators:
            if op in condition:
                parts = condition.split(op)
                if len(parts) == 2:
                    left = self.evaluate_expression(parts[0])
                    right = self.evaluate_expression(parts[1])
                    
                    if op == '=':
                        return left == right
                    elif op == '<>':
                        return left != right
                    elif op == '<=':
                        return left <= right
                    elif op == '>=':
                        return left >= right
                    elif op == '<':
                        return left < right
                    elif op == '>':
                        return left > right
        
        raise ValueError(f"Неверное условие: {condition}")

def main():
    if len(sys.argv) != 2:
        print("Использование: python basic.py program.bas")
        sys.exit(1)
    
    interpreter = BasicInterpreter()
    interpreter.load_program(sys.argv[1])
    interpreter.run()

if __name__ == "__main__":
    main()