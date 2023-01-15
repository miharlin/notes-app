import shelve
import datetime

class Format:
    underline = '\033[4m'
    end_underline = '\033[0m'

    green =  '\033[32m' #Green Text
    red = '\033[31m'
    blue = '\033[34m'
    grey = '\033[30m'
    end_color = '\033[m' # reset to the defaults

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
    def __init__(self, note_name, owner, current_time):
        self.text = ''
        self.note_name = note_name
        self.owner = owner
        self.last_changed = current_time
        self.user_last_changed = owner

    def append_text(self, text, username):
        self.text += " " + text
        self.last_changed = datetime.datetime.now()
        self.user_last_changed = username

    def replace_text(self, text, username):
        self.text = text
        self.last_changed = datetime.datetime.now()
        self.user_last_changed = username

class App:
    def __init__(self, db):
        self.db = db

    def signup(self, temp_user):
        with shelve.open(self.db) as db:
            if temp_user.username() not in db:
                db[temp_user.username()] = temp_user
                self.current_user = temp_user
                return True

    def login(self, temp_user):   #reorganize
        with shelve.open(self.db) as db:
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
        with shelve.open(self.db) as db:
            for i in range(1, db['note_count']+1):
                if str(i) in db:
                    key = str(i)
                    a = db[key]
                    if a.note_name == note_name and a.owner == self.current_user.username():
                        print('You already have note with this name.')
                        return
            a = Note(note_name, self.current_user.username(), datetime.datetime.now())
            db['note_count'] += 1
            key = str(db['note_count'])
            db[key] = a

    def delete_note(self, note_name):
        note_key = self.find_note(note_name)
        with shelve.open(self.db) as db:
            if note_key != None and note_key in db:
                del db[note_key]
                db['note_count'] -= 1
            else:
                print('Note not found.')

    def view_all_notes(self):
        with shelve.open(self.db) as db:
            if db['note_count'] == 0:
                print('no notes exist')
            else:
                print("Notes: ")
                for i in range(1, db['note_count']+1):
                    key = str(i)
                    if key in db:
                        a = db[key]
                        print(Format.underline+ a.note_name + Format.end_underline, ":", a.text)

    def view_personal_notes(self):
        with shelve.open(self.db) as db:
            if db['note_count'] == 0:
                print('no notes exist')
            else:
                print("Notes: ")
                for i in range(1, db['note_count']+1):
                    key = str(i)
                    if key in db:
                        a = db[key]
                        if a.owner == self.current_user.username():
                            print(Format.underline + a.note_name + Format.end_underline, ":", a.text)
                            print("(Last updated:", a.last_changed, "by", Format.red + a.user_last_changed + Format.end_color + ")")

    def find_note(self, note_name):#find and retrieve note key
        with shelve.open(self.db) as db:
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
                        with shelve.open(self.db) as db:
                            self.current_note = db[note_key]

                        text_action = input('''
                        Choose.
                        1. Append text
                        2. Replace text
                        ''')

                        text = input('Type text: ')

                        if text_action == '1':
                            self.current_note.append_text(text, self.current_user.username())

                        if text_action == '2':
                            self.current_note.replace_text(text, self.current_user.username())

                        with shelve.open(self.db) as db:  #save changes
                            db[note_key] = self.current_note

                    else:
                        print('Selected note does not exist.')

    def run(self):
        with shelve.open(self.db) as db:
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
