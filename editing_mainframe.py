import shelve

class User:
    def __init__(self, fname, lname, psw):
        self.fname = fname
        self.lname = lname

    def username(self):
        return self.fname + self.lname

    def create_note(self, note_name):
        a = Note(self.username())
        with shelve.open('app') as db:
            if note_name not in db:
                db[note_name] = a
            else:
                print('note already exists')

    def delete_note(self, note_name):
        with shelve.open('app') as db:
            if note_name in db:
                del db[note_name]
            else:
                print('Note not found.')

    def view_notes(self):
        with shelve.open('app') as db:
            print(list(db.keys()))
        #work on visualization

class Note:
    def __init__(self, user):
        self.text = ''
        self.user = user

    def append_text(self, text):
        self.text += text

    def replace_text(self, text):
        self.text = text

def create_account(temp_user):
    with shelve.open('app') as db:
        if temp_user.username() not in db:
            db[temp_user.username()] = temp_user
            return True #logged in

def login(temp_user):
    with shelve.open('app') as db:
        if temp_user.username() in db:
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
        temp_user = User(vals[0], vals[1], vals[2]) #temporary user being checked

        if choice == '1':
            if create_account(temp_user):
                current_user = temp_user
                print('account created.')
                break
            else:
                print('account already exists')

        if choice == '2':
            if login(temp_user):
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
            #print Notes

            choice = input('''
            Choose:
            1. View notes
            2. Create note
            3. Delete note
            4. Select note
            ''')

            if choice == '1':
                pass

            if choice == '2':
                note_name = input('Input name for note.')
                current_user.create_note(note_name)

            if choice == '3':
                note_name = input('Input name of note to delete.')
                current_user.delete_note(note_name)

            if choice == '4':
                selected_note = input('notename')
                with shelve.open('app') as db:
                    if selected_note in db:
                        current_note = db[selected_note]
                    else:
                        print('selected note does not exist.')
                if current_note != None:
                    text_action = input('1. Append text 2. Replace text')
                    text = input('Type text:')
                    if text_action == '1':
                        current_note.append_text(text)
                    if text_action == '2':
                        current_note.replace_text(text)


            #     note_name = input('Input name of note to append.')
            # if choice == '5':
            #     note_name = input('Input name of note to replace.')
            #     text = input('Input the replacement text.')
            #     current_note.replace_text(text)

main()

#notes: shelve currently works for single User, if multiple, re think keys
