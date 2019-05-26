This is a programm written on Python.

To run this code you need to have python on your computer. You need to write "python proga.py" in console.


HOW TO BUILD INTO ONE 'EXE' FILE:
To make one single 'exe' file you need 'pyinstaller' (to install it you need to write in console "pip install pyinstaller") also you need 'PIL' (to install it you need to write in console "pip install Pillow")
Also I attached file named 'for_build.spec'. You need it to build programm.
You need to open it and make some changes.
line 7: change 'Your path' to you path (where is this folder) like this one 'C:\\Users\\admin\\Desktop\\physics'
line 16: the same
line 29: the same

Further you need to write "pyinstaller for_build.spec" in console. It is not very fast process.
When it ends you will have folder "dist" and there lies 'exe' file.