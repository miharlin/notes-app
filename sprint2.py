import shelve
with shelve.open('app') as db:
    # print(list(db.keys()))
    if 'note_count' not in db:
        db['note_count'] = 0

class User:
    def __init__(self, fname, lname, psw):
        self.fname = fname
        self.lname = lname
        self.password = psw

    def username(self):
        return self.fname + self.lname


class Note:
    def __init__(self, note_name, owner):
        self.text = ''
        self.note_name = note_name
        self.owner = owner

    def append_text(self, text):
        self.text += text

    def replace_text(self, text):
        self.text = text

def create_note(current_user, note_name):
    a = Note(note_name, current_user.username())
    with shelve.open('app') as db:
        db['note_count'] += 1
        key = str(db['note_count'])
        db[key] = a

def delete_note(current_user, note_name):
    note_key = find_note(note_name, current_user.username())
    with shelve.open('app') as db:
        if note_key in db:
            del db[note_key]
            db['note_count'] -= 1
        else:
            print('Note not found.')

def view_notes(current_user):
    with shelve.open('app') as db:
        if db['note_count'] == 0:
            print('no notes exist')
        else:
            print("Notes: ")
            for i in range(1, db['note_count']+1):
                key = str(i)
                if key in db:   #crash prevention
                    a = db[key]
                    print(a.note_name, ":", a.text)
                    #work on visualization sprint3

def find_note(note_name, note_owner):#find and retrieve note key
    with shelve.open('app') as db:
        for i in range(1, db['note_count']+1):
            a = db[str(i)]
            if a.note_name == note_name and a.owner == note_owner:
                #allow collaborator access sprint3
                return str(i)

def cipher(entered_pw):
  shift = 1
  encrypted_string = ""
  for i in range(len(entered_pw)):
    shift_pw_value = ord(entered_pw[i]) + shift
    if ord('a') > shift_pw_value > ord('Z') or shift_pw_value > ord('z'):  #when shift brings out of ascii range
      shift_pw_value -= 26
    shift_pw_chr = chr(shift_pw_value)
    encrypted_string = encrypted_string + shift_pw_chr
  return encrypted_string

def create_account(temp_user):
    with shelve.open('app') as db:
        if temp_user.username() not in db:
            db[temp_user.username()] = temp_user
            return True #logged in

def login(temp_user):   #reorganize
    with shelve.open('app') as db:
        if temp_user.username() in db:
            a = db[temp_user.username()]
            if a.password == temp_user.password:
                current_user = db[temp_user.username()]
            return True
            #add authentification

def main():

    current_user = None
    current_note = None
    while True: #login

        choice = input('''
        Welcome to Notes on Notes.
        Choose:
        1. Create account
        2. Access account
        ''')

        vals = input('Input: firstname, lastname, password: ').split()
        temp_user = User(vals[0], vals[1], cipher(vals[2])) #temporary user being checked

        if choice == '1':
            if create_account(temp_user):
                current_user = temp_user
                print('account created.')
                break
            else:
                print('account already exists')

        if choice == '2':
            if login(temp_user):
                current_user = temp_user
                print('logged in.')
                break
            else:
                print('account does not exist')

    while True: #once logged in

        choice = input('''
        Choose:
        1. Global notes
        2. Personal notes
        ''')

        if choice == '1':
            pass

        if choice == '2':

            choice = input('''
            Choose:
            1. View notes
            2. Create note
            3. Delete note
            4. Select note
            ''')

            if choice == '1':
                view_notes(current_user)

            if choice == '2':
                note_name = input('Input name for note: ')
                create_note(current_user, note_name)

            if choice == '3':
                note_name = input('Input name of note to delete: ')
                delete_note(current_user, note_name)

            if choice == '4':
                selected_note = input('Input name of note: ')
                note_key = find_note(selected_note, current_user.username())
                if note_key:   #if exists
                    with shelve.open('app') as db:
                        current_note = db[note_key]

                    text_action = input('''
                    Choose.
                    1. Append text
                    2. Replace text
                    ''')

                    text = input('Type text: ')

                    if text_action == '1':
                        current_note.append_text(text)

                    if text_action == '2':
                        current_note.replace_text(text)

                    with shelve.open('app') as db:  #save changes
                        db[note_key] = current_note

                else:
                    print('Selected note does not exist.')

main()
