# Helios version: 1.3


This is the code for the Helios GPU Controller

Developers:

Lasse Müller, Bao Tran Nguyen, Berkehan Ünal

## Usage
### Requirements
Our solution was developed using Python. To run the software, these are the prerequisites:
* Operating system distribution of Windows or Linux
* Python >=3.8
* pip package installer (https://pip.pypa.io/en/stable/)
* Preferably a virtual environment

### Installation of Software and Dependencies
A development copy of the project's repository or software can be created using the following command.
```
$ git clone https://github.com/automl-private/MLProject_Mueller-Nguyen-Uenal_Helios
```

Python-specific extensions and modules are needed and can be found in the [Requirements.txt](./).
To install the modules, execute the following command from the /post-hoc-cbm folder:
```
$ pip install -r requirements.txt
```
To run PyTorch with cuda (NVIDIAs software for GPU management), PyTorch has to be installed from their [website](https://pytorch.org/get-started/locally/).


## Code Execution ##

```
Execute: gpu_controller = HeliosGPUController("conf.yaml")
```



## Testing ##
```
We used testpcbm.py and testheliosgpucontroller.py for unit testing.
```


## License ##

This project is licensed under the [MIT License](./LICENSE.md).

```
 _   _         _                       ___    ___    _   _     ___                  _                _    _                
( ) ( )       (_ )  _                 (  _`\ (  _`\ ( ) ( )   (  _`\               ( )_             (_ ) (_ )              
| |_| |   __   | | (_)   _     ___    | ( (_)| |_) )| | | |   | ( (_)   _     ___  | ,_) _ __   _    | |  | |    __   _ __ 
|  _  | /'__`\ | | | | /'_`\ /',__)   | |___ | ,__/'| | | |   | |  _  /'_`\ /' _ `\| |  ( '__)/'_`\  | |  | |  /'__`\( '__)
| | | |(  ___/ | | | |( (_) )\__, \   | (_, )| |    | (_) |   | (_( )( (_) )| ( ) || |_ | |  ( (_) ) | |  | | (  ___/| |   
(_) (_)`\____)(___)(_)`\___/'(____/   (____/'(_)    (_____)   (____/'`\___/'(_) (_)`\__)(_)  `\___/'(___)(___)`\____)(_)                                                                                                                                                                                                                                                
```
