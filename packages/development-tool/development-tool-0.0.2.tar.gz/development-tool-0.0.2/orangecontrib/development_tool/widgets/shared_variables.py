
# Currently active OWS
current_ows = "toto"

def get_current_ows():
    return current_ows
# Currently active OWS id
ptr_current_canvas_main = 0
# List of all OWS
vect_doc_ptr = []  # [path, id, first opening time]

# Vector containing the master external in the order of invocation
# Value is "cmd_line" if it's from the command line, otherwise it's the ID
ptr_master_external_orange = []

orange_data_table=None
tototata=3
zoubida=0
id_du_variable_pool=1
dict_label ={}# []# {}#{'Student Name': 'Berry', 'Roll No.': 12, 'Subject': 'English'}
dict_variable={}#{'a':123.456,'b':789.0123}
vect_label=[]
forbiden_string = ["/", '.', "|", ";","'",'"',"dict_variable","[","]",",","#"]
