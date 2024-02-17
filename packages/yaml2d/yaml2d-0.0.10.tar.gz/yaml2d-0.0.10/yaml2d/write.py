import itertools 

if __name__ == "__main__":
    from common import Entry, TAB, MINUS_TAB, NL, SEP, NaN
else:
    from .common import Entry, TAB, MINUS_TAB, NL, SEP, NaN


class Write():
    def __init__(self):
        self.buffer = ""
        self.last_keys = None
        self.max_buffer_size = 400
        self.is_writing_list = False
    
    def write_entry(self, entry):
        if entry.is_parent_value:
            self.buffer += entry.parent + SEP + entry.obj + NL
            self.buffer += NL
        elif entry.is_ylist:
            if not self.is_writing_list and entry.parent:  
                #parent check incase of append
                self.buffer += entry.parent + SEP + NL
            for i, keyval in enumerate(entry.obj.items()):
                key, val = keyval
                if i == 0:
                    key = MINUS_TAB + key
                else:
                    key = TAB + key
                item = TAB + key + SEP + val
                self.buffer += item + NL
        else:
            self.buffer += entry.parent + SEP + NL
            self.last_keys = entry.obj.keys()
            for i, keyval in enumerate(entry.items()):
                key, val = keyval
                item = TAB + key + SEP  + val
                self.buffer += item + NL
            self.buffer += NL
            
        self.is_writing_list = entry.is_ylist


    def write(self, path, entries, flag='w'):
        with open(path, flag) as f:
            for entry in entries:
                self.write_entry(entry)
                if len(self.buffer) > self.max_buffer_size:
                    f.write(self.buffer)
                    self.buffer = ""
            f.write(self.buffer)

            
def write_dataframe(path, df, name):
    itr = df.iterrows()
    itr = df.to_dict(orient="records")
    itr = map(lambda x: Entry.from_dict(parent=name, obj=x, is_ylist=True), itr)
    
    if df.attrs:
        itr = itertools.chain(Entry.dict2d_to_list(df.attrs), itr)

    write = Write()
    write.write(path, itr)


def write_dict2d(path, dict2d):
    itr = Entry.dict2d_to_list(df.attrs)
    write = Write()
    write.write(path, itr)

def append_write(path, dict1d):
    entry = Entry.from_dict(dict1d, parent=None, is_ylist=True)
    write = Write()
    write.write(path, [entry], flag='a')

if __name__ == "__main__":
    import pandas as pd

    data = {'Name': ['Alice', 'Bob', 'Charlie'],
            'Age2': [25, 30, 22],
            'Age':  [25, 30, 22],
            'City': ['New York', 'San Francisco', 'Los Angeles']}

    df = pd.DataFrame(data)
    df.attrs = {'x': 32323.3}
    df.attrs['liest'] = [12,33,45,353]
    write_dataframe('./out.yaml', df, "dataie")
    write_dict2d('./dict2d.yaml', df.attrs)
    append_write('./out.yaml', {"Appended": "Appended",
    "Age2": 22,
    "Age": 22,
    "City": "Los Angeles"})
