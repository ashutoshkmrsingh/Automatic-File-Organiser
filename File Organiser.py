# Required libraries
import os 
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from win10toast import ToastNotifier

#target_path = 'D:\check'
target_path = r'C:\Users\hp\Downloads'

toaster = ToastNotifier()
toaster.show_toast(title='File Organiser', msg='Orgainising Files in {}'.format(target_path), duration=10)

# Target Folder
os.chdir(target_path)

folder_count = 0 
for entry in os.scandir():
    if entry.is_dir():
            folder_count+=1

start_time = 'First_time' # to check wether script start first time or not

try:
    with open('start.bin', 'r') as file:
        prev_folder_count = file.read()
        start_time = 'Started'
except FileNotFoundError:
    with open('start.bin', 'w') as file:
        file.write('started')
except PermissionError:
    print('Run As Administrator')

# Default Folders
folders = {
    'Java':['.java', '.class', '.xrb', '.jar', 'jsp', '.dpj'],
    'C C++':['.c','.cpp', '.cxx', '.exe', '.hrc', '.inc', '.c++'],
    'HTML CSS': ['.html5', '.html', '.htm', '.xhtml', '.css'], 
    'Image': ['.jpeg', '.jpg', '.tiff', '.gif', '.bmp', '.png', '.bpg', '.svg', 
               '.heif', '.psd'], 
    'Video': [".avi", ".flv", ".wmv", ".mov", ".mp4", ".webm", ".vob", ".mng", 
               ".qt", ".mpg", ".mpeg", ".3gp"], 
    'Document': [".oxps", ".epub", ".pages", ".docx", ".doc", ".fdf", ".ods", 
                  ".odt", ".pwi", ".xsn", ".xps", ".dotx", ".docm", ".dox", 
                  ".rvg", ".rtf", ".rtfd", ".wpd", ".xls", ".xlsx", ".ppt", 
                  ".pptx", ".csv"], 
    'Archive': [".a", ".ar", ".cpio", ".iso", ".tar", ".gz", ".rz", ".7z", 
                 ".dmg", ".rar", ".xar", ".zip"], 
    'Audio': [".aac", ".aa", ".aac", ".dvf", ".m4a", ".m4b", ".m4p", ".mp3", 
              ".msv", "ogg", "oga", ".raw", ".vox", ".wav", ".wma"], 
    'Text': [".txt", ".in", ".out"], 
    'Pdf': [".pdf"], 
    'Python': [".py", 'pyc'], 
    'XML': [".xml"], 
    'Exe Setup': ['.exe', '.msi'], 
    'Shell': ['.sh', '.bash'],
    'Jupyter':['.ipynb'],
    'ASM':['.asm'],
    'Icon':['.ico'],
    'SQL':['.sql', '.db', '.sqlite3']
} 

# File Extension to Directory Mapping
file_extension_to_dir = {extension: folder for folder, file_extension in folders.items() for extension in file_extension}

def organize_file():
    for item in os.scandir(): # check if item is folder or file
        if item.is_dir(): 
            continue
        file_path = Path(item) # file name
        file_format = file_path.suffix.lower() # file extension
        if file_format in file_extension_to_dir: 
            try:
                directory_path = Path(file_extension_to_dir[file_format]) # generate Target Folder
                directory_path.mkdir(exist_ok=True)                       # make Target Folder
                file_path.rename(directory_path.joinpath(file_path))      # move file to target folder
            except FileExistsError:
                continue
            
if start_time == 'First_time':  
    organize_file()
    
else:
    # mapping existing file and path
    d = {
    'File':[],
    'Target':[]    
    }

    for path, dirs, files in os.walk(target_path):
        for file in files:
            d['File'].append(file)
            d['Target'].append(path)
            
    df = pd.DataFrame(d) # datafame of file and its path
    
    df['File'] = df['File'].apply(lambda file_name: ''.join(file_name.split('.')[-1]).lower()) # Extracting file extension
    
    le = LabelEncoder()
    df['File'] = le.fit_transform(df['File'].values)
    df['Target'] = le.fit_transform(df['Target'].values)
    
    df_2 = pd.DataFrame(d)
    df_2['File'] = df_2['File'].apply(lambda file_name: ''.join(file_name.split('.')[-1]).lower())
    df_2['File_encoded'] = le.fit_transform(df_2['File'].values)
    df_2['Target_encoded'] = le.fit_transform(df_2['Target'].values)

    file_to_encode={}

    for file in df_2["File"].unique():
        file_to_encode[file] =  df_2[df_2["File"]==file].File_encoded.values[0]

    target_to_encode={}

    for tar in df_2["Target"].unique():
        target_to_encode[tar] =  df_2[df_2["Target"]==tar].Target_encoded.values[0]

    encode_to_file = {}

    for file, code in file_to_encode.items():
        encode_to_file[code]=file

    encode_to_target = {}

    for file, code in target_to_encode.items():
        encode_to_target[code]=file
    
    X_ = df['File'].values
    X = X_.reshape(-1, 1)
    y = df['Target'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05)
    
    neighbor, score = 0, 0

    for n in range(1,6):
        knn = KNeighborsClassifier(n_neighbors=n)
        knn.fit(X_train, y_train)
        score_ = knn.score(X_test, y_test)
        if score_ >= score:
            score = score_
            neighbor = n

    knn = KNeighborsClassifier(n_neighbors=n)

    knn.fit(X_train, y_train)

    for item in os.scandir(): # check if item is folder or file
        if item.is_dir(): 
            continue
        file_path = Path(item) # file name
        file_format = file_path.suffix.lower() # file extension
        if file_format != '.bin':
            try:
                file = file_to_encode[file_format[1:]]
                file_path.rename(str(encode_to_target[knn.predict(np.array([[file]]))[0]])+ "\\" + str(file_path))
            except KeyError:
                organize_file()
            except FileExistsError:
                continue

# remove empty folders:
for dir in os.scandir(): 
    try: 
        os.rmdir(dir) 
    except: 
        pass

folder_count = 0 
for entry in os.scandir():
    if entry.is_dir():
            folder_count+=1
    
try:
    with open('start.bin', 'w') as file:
        file.write(str(folder_count))
except PermissionError:
    print('Run as Administrator')
toaster.show_toast(title='File Organiser', msg='{} Organised Successfully'.format(target_path), duration=10)
