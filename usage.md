# Usage
After the package has been installed, just use:

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
   