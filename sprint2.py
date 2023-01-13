import shelve

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

class App:
    def __init__(self, db):
        self.db = db

    def signup(self, temp_user):
        with shelve.open('app') as db:
            if temp_user.username() not in db:
                db[temp_user.username()] = temp_user
                self.current_user = temp_user
                return True

    def login(self, temp_user):   #reorganize
        with shelve.open('app') as db:
            if temp_user.username() in db:
                a = db[temp_user.username()]
                if a.password == temp_user.password:
                    self.current_user = db[temp_user.username()]
                    return True

    def set_account(self):  #login/signup
        logged_in = False
        while logged_in == False:
            choice = input('''
            Choose:
            1. Signup
            2. Login
            ''')

            vals = input('Input: firstname, lastname, password: ').split()
            temp_user = User(vals[0], vals[1], cipher(vals[2])) #temporary user being checked

            if choice == '1':
                if self.signup(temp_user):
                    logged_in = True
                else:
                    print('Account already exists.')

            if choice == '2':
                if self.login(temp_user):
                    logged_in = True
                else:
                    print('Account does not exist.')

    def create_note(self, note_name):
        with shelve.open('app') as db:
            for i in range(1, db['note_count']+1):
                if str(i) in db:
                    key = str(i)
                    a = db[key]
                    if a.note_name == note_name and a.owner == self.current_user.username():
                        print('You already have note with this name.')
                        return
            a = Note(note_name, self.current_user.username())
            db['note_count'] += 1
            key = str(db['note_count'])
            db[key] = a

    def delete_note(self, note_name):
        note_key = self.find_note(note_name)
        with shelve.open('app') as db:
            if note_key in db:
                del db[note_key]
                db['note_count'] -= 1
            else:
                print('Note not found.')

    def view_all_notes(self):
        with shelve.open('app') as db:
            if db['note_count'] == 0:
                print('no notes exist')
            else:
                print("Notes: ")
                for i in range(1, db['note_count']+1):
                    key = str(i)
                    if key in db:
                        a = db[key]
                        print(a.note_name, ":", a.text)
                        #work on visualization sprint3

    def view_personal_notes(self):
        with shelve.open('app') as db:
            if db['note_count'] == 0:
                print('no notes exist')
            else:
                print("Notes: ")
                for i in range(1, db['note_count']+1):
                    key = str(i)
                    if key in db:
                        a = db[key]
                        if a.owner == self.current_user.username():
                            print(a.note_name, ":", a.text)
                            #work on visualization sprint3

    def find_note(self, note_name):#find and retrieve note key
        with shelve.open('app') as db:
            for i in range(1, db['note_count']+1):
                if str(i) in db:
                    a = db[str(i)]
                    if a.note_name == note_name and a.owner == self.current_user.username():
                        #allow collaborator access sprint3
                        return str(i)

    def menu(self):
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
                    self.view_personal_notes()

                if choice == '2':
                    note_name = input('Input name for note: ')
                    self.create_note(note_name)

                if choice == '3':
                    note_name = input('Input name of note to delete: ')
                    self.delete_note(note_name)

                if choice == '4':
                    selected_note = input('Input name of note: ')
                    note_key = self.find_note(selected_note)
                    if note_key:   #if exists
                        with shelve.open('app') as db:
                            self.current_note = db[note_key]

                        text_action = input('''
                        Choose.
                        1. Append text
                        2. Replace text
                        ''')

                        text = input('Type text: ')

                        if text_action == '1':
                            self.current_note.append_text(text)

                        if text_action == '2':
                            self.current_note.replace_text(text)

                        with shelve.open('app') as db:  #save changes
                            db[note_key] = self.current_note

                    else:
                        print('Selected note does not exist.')

    def run(self):
        with shelve.open('app') as db:
            # print(list(db.keys()))
            if 'note_count' not in db:
                db['note_count'] = 0
        self.set_account()
        self.menu()

def main():
    print('Welcome to Notes on Notes.')
    a = App('app')
    a.run()
    #shelve 'app' incase of crash

main()
