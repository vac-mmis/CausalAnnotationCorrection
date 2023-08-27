A tool support tool for inspection, validation and correction of behavioral annotations. For more information, visit the project website:
> https://github.com/vac-mmis/CausalAnnotationCorrection

The tool requires Python 3.8 or higher.

### How to use it?
Install the package using pip:

```
$ pip install acheck
```
After the installation, use:
```
$ acheck check $domain.pddl $problem.pddl $annotation.csv
```
By default, it will automatically start a local server on [127.0.0.1:9000](http://127.0.0.1:9000/).
#### Options:  
- `-l $file_1 $file_2 $file_n` : Enter one or multiple annotation files or the domain or problem file to lock them in editor
    ```
    $ acheck check domain.pddl problem.pddl anno_1.csv -l domain.pddl anno_1.csv
    ```

- `-o $directory`: Enter a custom directory for all output files. 
    ```
    $ acheck check domain.pddl problem.pddl anno_1.csv -o project/output
    ```
- `-p port`: Specify the `port` on which the server is running. 
    ```
    $ acheck check domain.pddl problem.pddl anno_1.csv -p 8000
    ```
- `-v`: Enable verbose output. 

- `-m directory`: Enter a custom `directory` to load multiple annotations

- `--nogui`: For command line only use. 

- `--inplace`: Work with the original files. For command line only use without backup. 

### Enchant
The tool uses `pyenchant` for spell checking. It is a spellchecking library for Python, based on the [Enchant](https://abiword.github.io/enchant/) library. In order to work properly you will need to install the Enchant C library manually:

**MacOS:** 
  ```
  $ brew update
  $ brew install enchant
  ```
To avoid problems, restart your system after installation.

**Linux:**\
The quickest way is to install `libenchant` using the package manager of your current distribution.\
To detect the libenchant binaries, PyEnchant uses `ctypes.util.find_library()`, which requires `ldconfig`, `gcc`, `objdump` or `ld` to be installed. This is the case on most major distributions, however statically linked distributions (like Alpine Linux) might not bring along `binutils` by default.\
To avoid problems, restart your system after installation.
   ```
   $ pacman -S enchant
   
   $ sudo apt-get install enchant-2
   ````

If you experience any issues, you may want to have a look at: 
> https://pyenchant.github.io/pyenchant/install.html

It can happen that with the enchant installation, no providers are installed that enable the spell check. 
For this you can install the desired provider yourself:
```
$ pacman -S aspell

$ sudo apt-get install aspell
```
Also the desired languages can be installed in this way:
```
$ pacman -S aspell-en
$ pacman -S aspell-de

$ sudo apt-get install aspell-en
$ sudo apt-get install aspell-de
```
If you experience any issues, you may want to have look at:
>https://pyenchant.github.io/pyenchant/install.html#installing-a-dictionary

The standard language for the spell checker is English (en_US). You need to configure the language with the following command:
```
$ acheck config -l $language
```
Supported languages (at the moment): `en_US` `en_GB` `de_DE`


 
### Plan Validation
If you want to enable plan validation, you need to download the [KCL Validator](https://github.com/KCL-Planning/VAL). Just follow the instructions on the GitHub page and download the binaries for you operating system. 
To get to the download, just click on the `Azure Pipelines` button at the beginning of the [README.md](https://github.com/KCL-Planning/VAL/blob/master/README.md). Save the binaries in a location that suits you.
After downloading, you need to configure the path to the validator executable file. `bin/Validate` or `bin/Validate.exe`

In order to use the plan validator correctly, stop the tool and set the path like:
```
$ acheck config -v $path-to-validate-executable
```
Examples:
```
$ acheck config -v /Users/macos64/Val-20211204.1-Darwin/bin/Validate
$ acheck config -v /Users/linux/Val-20211204.1-Linux/bin/Validate
$ acheck config -v /Users/windows/Val-20211204.1-Windows/bin/Validate.exe
```