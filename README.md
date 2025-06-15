# ActionKeys
ActionKeys is a Python project that allows you to expand your keyboard with an Arduino extra keyboard.

## Functionality
Using the first button, you can Google selected on your screen text. Script imitates Ctrl+C shortcut and opens a tab in 
your browser.

Using the second button, you can have Ollama response to selected text. 

Clicking on both of the buttons, the Ollama chat window will pop up.

You are able to change buttons functionality by changing the corresponding code in button_script directory.

## Installation and running
If you are using Debian based linux distro, make sure to install the following packages:
```bash
sudo apt install xclip
sudo apt install libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-cursor0
```
Also, make sure you installed Ollama and gemma3:4b model (you will be able to choose model from GUI in future updates, now you 
can change it in code only).

1. Clone this GitHub repository:
```bash
git clone https://github.com/lopolen/ActionKeys.git
```
2. Create venv in repository directory:
```bash
cd ActionKeys
python3 -m venv .venv
```
3. Install requirements:
```bash
source .venv/bin/activate
pip3 install -t requirements.txt
deactivate
```
4. Run RootAPI.py with root permissions:
```bash
sudo .venv/bin/python3 RootAPI.py
```
If you are using Windows, you can run RootAPI.py without privileges, but if you are going to make any changes that may 
require admin rights, you should run it with root, obviously.  
5. In another terminal, run main.py WITHOUT sudo:
```bash
.venv/bin/python3 main.py 
```
6. Congrats, you successfully launched ActionKeys :)

## Q&A
- Why do I need to run RootAPI.py with sudo?
- - **It is necessary to get access to Arduino serial port and to imitate keyboard shortcuts.**


- Why do there two Python scripts to run? Why not only one?
- - **I wanted to separate code, which needs root privileges and code which not. These two scripts comunicate with each other by localhost TCP** 
