if __name__ != '__main__':
    raise RuntimeError("Don't import this as a module.")

import pprint

lisp_to_mei_accid_dict = {
    'DOUBLE-FLAT': 'ff',
    'THREE-Q-FLAT': '3qf',
    'FLAT': 'f',
    'SEMI-FLAT': '1qf',
    'NATURAL': '',
    'SEMI-SHARP': '1qs',
    'SHARP': 's',
    'THREE-Q-SHARP': '3qs',
    'DOUBLE-SHARP': 'x'
    }


lisp_pitch_class_to_mei_dict = {
    0: 'c',
    1: 'd',
    2: 'e',
    3: 'f',
    4: 'g',
    5: 'a',
    6: 'b'
}

def add_line_to_inbound_lookup_dict(current_language_dict, line):
    stripped_line = line.strip()
    split_line = line.split()
    lisp_pitch_token = split_line[0][1:]
    lisp_pitch_class_number = int(split_line[4])
    lisp_accid_string = split_line[5][:-2]
    the_tuple = (
        lisp_pitch_class_to_mei_dict[lisp_pitch_class_number],
        lisp_to_mei_accid_dict[lisp_accid_string]
        )
    current_language_dict[lisp_pitch_token] = the_tuple



def parse_languages(lines):
    inbound_languages_dict = {}
    current_language = None
    for line in lines:
        if line[:5] == '    (' :
            stripped_line  = line.strip()
            split_line = stripped_line.split()
            current_language = split_line[0][1:]
            inbound_languages_dict[current_language] = {}
        elif 'ly:make-pitch' in line:
            add_line_to_inbound_lookup_dict(inbound_languages_dict[current_language], line)
    return inbound_languages_dict

#dictionary structure is a dict of dicts like {'nederlands':{'as':('a','f')}}
#from that line, skip ahead 1 line and read the language name
#skip ahead one more line and compile the lookup dict
#return the complete dictionary if you get to two blank lines in a row

theFile = open('noteNames.txt', 'r')
lines = theFile.readlines()
inbound_languages_dict =  parse_languages(lines)
pprint.pprint(inbound_languages_dict, indent=4)