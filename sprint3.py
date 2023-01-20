import shelve
import datetime

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

class Format:
    underline = '\033[4m'
    end_underline = '\033[0m'

    green =  '\033[32m' #Green Text
    red = '\033[31m'
    blue = '\033[34m'
    grey = '\033[30m'
    end_color = '\033[m' # reset to the defaults

class User:
    def __init__(self, fname, lname, psw):
        self.password = psw
        self.username = fname + lname

class Note: #notes and comments
    def __init__(self, owner, note_name=None):
        self.text = ''
        self.note_name = note_name
        self.owner = owner
        self.comments = []
        self.last_changed = datetime.datetime.now()
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
            if temp_user.username not in db:
                db[temp_user.username] = temp_user
                self.current_user = temp_user
                return True

    def login(self, temp_user):
        with shelve.open(self.db) as db:
            if temp_user.username in db:
                if db[temp_user.username].password == temp_user.password:
                    self.current_user = db[temp_user.username]
                    return True

    def set_account(self):  #login/signup
        self.current_user = None
        while self.current_user == None:
            choice = input('''
        Choose:
        1. Signup
        2. Login
            ''')

            vals = input('Input: firstname, lastname, password: ').split()
            temp_user = User(vals[0], vals[1], cipher(vals[2])) #temporary user being checked

            if choice == '1':
                if not self.signup(temp_user):
                    print('Account already exists.')

            if choice == '2':
                if not self.login(temp_user):
                    print('Account does not exist.')
        self.menu()

    def create_note(self, note_name):
        with shelve.open(self.db) as db:
            for i in range(1, db['note_count']+1):
                if str(i) in db:
                    if db[str(i)].note_name == note_name and db[str(i)].owner == self.current_user.username:
                        print('You already have note with this name.')
                        return

            a = Note(self.current_user.username, note_name)
            db['note_count'] += 1
            db[str(db['note_count'])] = a

    def delete_note(self, note_name):
        note_key = self.find_note(note_name, self.current_user.username)
        with shelve.open(self.db) as db:
            if note_key != None and note_key in db:
                del db[note_key]
                db['note_count'] -= 1
            else:
                print('Note not found.')

    def create_comment(self):
        vals = Input('Input note name, note owner, comment text: ').split()

        note_key = self.find_note(vals[0], vals[1])
        if note_key:
            with shelve.open(self.db) as db:
                self.current_note = db[note_key]

                #create comment
                a = Note(self.current_user)
                a.append_text(vals[3], self.current_user)

                #save comment and store
                db['note_count'] += 1
                db[str(db['note_count'])] = a

                self.current_note.comments.append(a)
                db[note_key] = self.current_note

    def view_global_notes(self):
        with shelve.open(self.db) as db:
            if db['note_count'] == 0:
                print('No notes exist.')
            else:
                print("Notes: ")
                for i in range(1, db['note_count']+1):
                    if str(i) in db:
                        if db[str(i)].note_name:  #print notes, not comments
                            print(Format.underline + db[str(i)].note_name + Format.end_underline, ":", db[str(i)].text)
                            print('By:', db[str(i)].owner)

    def view_personal_notes(self):
        with shelve.open(self.db) as db:
            print("Notes: ")
            count = 0
            for i in range(1, db['note_count']+1):
                if str(i) in db:
                    if db[str(i)].note_name and db[str(i)].owner == self.current_user.username:#check if a note, then if correct user
                        count += 1
                        print(Format.underline + db[str(i)].note_name + Format.end_underline, ":", db[str(i)].text)
                        print("(Last updated:", db[str(i)].last_changed, "by", Format.red + db[str(i)].user_last_changed + Format.end_color, ")")

                        if len(db[str(i)].comments) > 0:    #if comments, print
                            print("     Comments:")
                            for comment in db[str(i)].comments:
                                print("         -", comment.text)
            if count == 0:
                print('No notes exist.')

    def find_note(self, note_name, owner):#find and retrieve note key
        with shelve.open(self.db) as db:
            for i in range(1, db['note_count']+1):
                if str(i) in db:
                    if db[str(i)].note_name == note_name and db[str(i)].owner == owner:
                        return str(i)

    def global_notes_actions(self):
        while True:
            self.view_global_notes()

            choice2 = input('''
                Choose:
                1. Comment on note
                2. Go back
            ''')

            if choice2 == '1':
                self.create_comment()

            if choice2 == '2':
                return

    def personal_notes_actions(self):
        while True:
            choice2 = input('''
            Choose:
            1. View notes
            2. Create note
            3. Delete note
            4. Edit note
            5. Go Back
            ''') #and view comments? or select? delete?

            if choice2 == '1':
                self.view_personal_notes()

            if choice2 == '2':
                note_name = input('Input name for note: ')
                self.create_note(note_name)

            if choice2 == '3':
                note_name = input('Input name of note to delete: ')
                self.delete_note(note_name)

            if choice2 == '4':
                selected_note = input('Input name of note: ')
                note_key = self.find_note(selected_note, self.current_user.username)
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
                        self.current_note.append_text(text, self.current_user.username)

                    if text_action == '2':
                        self.current_note.replace_text(text, self.current_user.username)

                    with shelve.open(self.db) as db:  #save changes
                        db[note_key] = self.current_note

                else:
                    print('Selected note does not exist.')

            if choice2 == '5':
                break

    def menu(self):
        while True: #once logged in

            choice1 = input('''
        Choose:
        1. Global notes
        2. Personal notes
        3. Logout
            ''')

            if choice1 == '1':
                self.global_notes_actions()

            if choice1 == '2':
                self.personal_notes_actions()

            if choice1 == '3':
                self.set_account()

    def run(self):
        with shelve.open(self.db) as db:
            if 'note_count' not in db:
                db['note_count'] = 0

        self.set_account()

def main():
    print('Welcome to Notes on Notes.')
    a = App('app')
    a.run()

main()
