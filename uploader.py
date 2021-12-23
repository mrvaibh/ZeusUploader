from tkinter import Button, Label, Tk, messagebox
from tkcalendar import DateEntry
import csv, pyodbc, requests, os

# Creating GUI
root = Tk()

root.iconbitmap('logo.ico')
root.geometry('500x250')
root.title('Zeus Uploader')
root.focus()

class CustomDateEntry(DateEntry):
    def _select(self, event=None):
        date = self._calendar.selection_get()
        if date is not None:
            self._set_text(date.strftime('%d/%m/%Y'))
            self.event_generate('<<DateEntrySelected>>')
        self._top_cal.withdraw()
        if 'readonly' not in self.state():
            self.focus_set()

from_date = Label(root, text='From:', font=("Helvetica", 15))
from_date.pack(pady=10)
from_cal = CustomDateEntry(root, selectmode='day', font=("Helvetica", 12))
from_cal._set_text(from_cal._date.strftime('%d/%m/%Y'))
from_cal.pack()

to_date = Label(root, text='To:', font=("Helvetica", 15))
to_date.pack(pady=10)
to_cal = CustomDateEntry(root, selectmode='day', font=("Helvetica", 12))
to_cal._set_text(to_cal._date.strftime('%d/%m/%Y'))
to_cal.pack()


# function to upload data within given range
def upload_data():
    # set up some constants
    FROM_DATE = from_cal.get_date()
    TO_DATE = to_cal.get_date()

    MDB = r'C:\Users\Vaibhav\OneDrive\Desktop\mdbbb\att2000.mdb'
    DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
    PWD = 'pw'
    SERVER_URL = 'http://demo.zeustech.in:8082/webapi/checkInOut/file/upload'

    if os.path.exists('config.zeus'):
        with open('config.zeus', 'r') as file:
            lines = file.read().splitlines()

            MDB = lines[0] # file directory
            DRV = '{' + lines[1] + '}' # type ODBC in start menu
            PWD = lines[2] # Password (if any)
            SERVER_URL = lines[3] # server endpoint


    # connect to db
    con = pyodbc.connect(f'DRIVER={DRV};DBQ={MDB};PWD={PWD}')
    cur = con.cursor()

    # run a query and get the results
    SQL = f'SELECT `userid`, `checktime`, `sensorid` FROM `checkinout` WHERE `checktime`>=#{FROM_DATE}# AND `checktime`<=#{TO_DATE}#;'
    rows = cur.execute(SQL).fetchall()

    if rows == []:
        messagebox.showwarning("Warning","No punch record for selected days")
        root.destroy()
        exit()

    export = []

    for row in rows:
        SQL_QUERY = f'SELECT `Badgenumber` FROM `userinfo` WHERE `userid`={row[0]};'
        badge_num = cur.execute(SQL_QUERY).fetchall()

        export.append({
            'Badgenumber': badge_num[0][0].zfill(5),
            'blank1': '',
            'Checktime': row[1].strftime("%d-%m-%Y %H:%M"),
            'blank2': '',
            'Sensorid': row[2]
        })
    cur.close()
    con.close()


    # creating CSV out of `export`
    with open('mytable.csv', 'w') as file:
        field_names = ['Badgenumber', 'blank1', 'Checktime', 'blank2', 'Sensorid']
        csv_writer = csv.DictWriter(file, fieldnames=field_names, delimiter=',', lineterminator='\n') # default field-delimiter is ","
        csv_writer.writerows(export)


    # send file to the server
    response_code = None
    with open('mytable.csv', 'r') as file:
        data = file.read()
        response = requests.post(SERVER_URL, data=data)
        response_code = response.status_code

    # Deleting the file immediately
    os.remove('mytable.csv')

    if response_code == 200:
        print('File upload was successful')
        messagebox.showinfo("Success","File upload was successful")
    else:
        print('Error in uploading data')
        messagebox.showerror("Error", "Error in uploading data to server")

    root.destroy()
    exit()



Button(root, text='Upload Data', command=upload_data, font=("Helvetica", 12)).pack(pady=25)

root.mainloop()