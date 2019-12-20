import zipfile
import os, os.path

OUTPUT = "data/traffic_flow_all/"
print("Files: " + str(len([name for name in os.listdir(OUTPUT) if os.path.isfile(name)])))
errors = []
i = 0
for filename in os.listdir(OUTPUT):
    if filename.endswith(".zip"):
        try:
            with zipfile.ZipFile(OUTPUT+filename,"r") as zip_ref:
                zip_ref.extractall(OUTPUT+"csv/")

            i += 1

            if i % 1000 == 0:
                print("Processed: "  + str(i))

        except:
            print("Error processing file " + filename)
            os.rename(OUTPUT+filename, OUTPUT+"error/"+filename)
