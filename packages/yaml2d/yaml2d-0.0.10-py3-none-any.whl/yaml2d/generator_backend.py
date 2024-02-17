from ast import literal_eval

if __name__ == "__main__":
    from read import Read
else:
    from .read import Read


def _python_eval(value):
    return literal_eval(value)

def _python_generator_backend(out, is_last, current_parent, yaml_obj,  list_counter, ytypes):
    if is_last:
        return out
    yaml_obj = {k: _python_eval(v) for k, v in yaml_obj.items()}
    return yaml_obj


def read2gen(stryaml2d):
    lines = stryaml2d.splitlines()
    read = Read( _python_generator_backend, is_onelist=False, tgt_parent='data')
    return read.read_generator(lines)


if __name__ == "__main__": 
    yamlf = """
config1:
  key1: 'value1'
  key2: 'value2'
  key3: 'value3'

config2:
  keyA: 'valueA'
  keyB: 'valueB'
  keyC: 'valueC'

data:
  - name: 'John Doe'
    age: 30
    city: 'New York'
  - name: 'Jane Smith'
    age: 25
    city: 'San Francisco'
  - name: 'Bob Johnson'
    age: 35
    city: 'Chicago'
  - name: 'Test'
    age: 35.0
    city: 'Chicago'
    """
    out = read2gen(yamlf)
    for item in out:
        print(item)