def setup_project():
    import os

    print("This will create a new project setup in the current directory. \n")
    project_name = str(input("Project Name: "))
    
    print("Creating Project Directory...")
    os.mkdir(os.path.join(os.getcwd(), project_name))
    new_working_dir = f"{os.getcwd()}/{project_name}"


    print("Creating Scenes Directory...")
    os.mkdir(os.path.join(new_working_dir, "scenes"))

    print("Creating Scripts Directory...")
    os.mkdir(os.path.join(new_working_dir, "scripts"))
    
    print("Creating main.py...")
    main_file = open(f"{project_name}/main.py", "w")
    main_file.write("""
        import pygame, json, os, sys

        from pyredengine import *
        from pyredengine import SceneService as SceneService

        class Main(App):
            def __init__(self):
                super().__init__()
            
            def load_scenes(self):
                # Read Docs 
                pass
                
        if __name__ == "__main__":
            main = Main()
            main.run()
    """)
    main_file.close()

    print("Creating config.json...")
    x = open(f"{project_name}/config.json", "w")
    x.write("""
    {
        "app": {
            "settings": {
                "resolution": "1280x720",
                "v-sync": 0,
                "max-fps": 60,
                "window-title-name": "",
                "window-icon-path": "",
                "start-scene": ""
            }
        }
    }
    """)
    x.close()

    make_bat = input("Would you like a .bat file for easy debugging? (Y/N): ")
    if make_bat == "Y":
        print("Creating run.bat...")
        y = open(f"{project_name}/run.bat", "w")
        y.write("""
            py main.py
            pause
        """)
        y.close()
    else:
        pass

    print("Finished Creating Project.")
    print("Read Docs for more info.")
    
