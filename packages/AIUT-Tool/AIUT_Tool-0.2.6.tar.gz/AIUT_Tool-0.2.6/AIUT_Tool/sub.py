# import AIUT_Core_Java as AIUT_Java
# import AIUT_Core_CSharp as AIUT_CSharp
import os, time
from AIUT_Tool import AIUT_Core_Java as AIUT_Java
from AIUT_Tool import AIUT_Core_CSharp as AIUT_CSharp


def loop(a,b,c, d):
    CSV_FILE_PATH = c
    FILE_PROCESSING_LOG = d
    code = False
    for currentpath, folders, files in os.walk(a):
        for file in files:
            #print(os.path.join(currentpath, file))
            f = os.path.join(currentpath, file)
            #for filename in os.listdir(a):
            #time.sleep(10)
            # if a[-1] != '\\':
            #     a += '\\'
            # f = a + filename
            print("From Sub.py "+f)
            if os.path.isfile(f):
                print(f)
                if validate_file(f,b,FILE_PROCESSING_LOG):
                    if b == "JUnit":
                        code = AIUT_Java.generate_unit_cases(f, b)
                    elif b == "NUnit" or b == "MSTest":
                        code = AIUT_CSharp.generate_unit_cases(f, b)

                    if code != False:
                        print("From Sub.py "+ code)
                    else:
                        print("Error!", "Error Generating Test Cases. Please retry!")
    # f = open(CSV_FILE_PATH, "a+")
    # f.write(code+"\n")
    # f.close()
                    create_file(CSV_FILE_PATH, code)
    return

def validate_file(filename, framework, logpath):
    FILE_PROCESSING_LOG = logpath
    message = None
    if os.path.isdir(filename):
        message = f"This is a directory {filename}," \
                  f"Not Processed."
        create_file(logpath, message)
        return False
    else:
        file_extension = os.path.splitext(filename)[1]
        file_size =  os.path.getsize(filename)
        if framework == "JUnit":
            if file_extension.lower() == ".java" and file_size > 0:
                message = f"This is a valid java file {filename}," \
                          f"Processed."
                create_file(logpath, message)
                return True
            else:
                message = f"This is not a valid java file {filename}," \
                          f"Not Processed."
                create_file(logpath, message)
                return False
        elif framework == "NUnit" or framework == "MSTest":
            if file_extension.lower() == ".cs" and file_size > 0:
                message = f"This is a valid csharp file {filename}," \
                          f"Processed."
                create_file(logpath, message)
                return True
            else:
                message = f"This is not a valid csharp file {filename}," \
                          f"Not Processed."
                create_file(logpath, message)
                return False

def create_file(path, message):
    f = open(path, "a+")
    f.write(message + "\n")
    f.close()

def get_test_gen_result_path(framework,run_id):
    import datetime
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d")
    parent_dir = "./"
    folder = "TestCreation_Record"
    folder_path = os.path.join(parent_dir, folder)
    os.makedirs(folder_path, exist_ok = True)
    os.makedirs(f"{folder_path}/{timestamp}", exist_ok=True)
    test_gen_result_path = f"{folder_path}/{timestamp}"
    CSV_FILE_PATH = f"{test_gen_result_path}/{framework}_TestGen_{run_id}.csv"
    TEST_RUN_LOG_PATH = f"{test_gen_result_path}/{framework}_TestRun_{run_id}.log"
    FILE_PROCESSING_LOG = f"{test_gen_result_path}/{framework}_File_Processing_{run_id}.log"
    return CSV_FILE_PATH, TEST_RUN_LOG_PATH, FILE_PROCESSING_LOG

if __name__=="__main__":
    #Get Timestamp
    import datetime
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    print(get_test_gen_result_path("JUnit",timestamp))
    
