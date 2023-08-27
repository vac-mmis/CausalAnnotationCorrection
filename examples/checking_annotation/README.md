### Annotation correction
You can use the tool to check annotations for errors and correct them if necessary. For this purpose, a correct domain and problem description is required. A simple example can be found at `examples/checking_annotation`.

```
$ acheck check shoes_d.pddl shoes_p1.pddl shoes.csv -l shoes_d.pddl shoes_p1.pddl
```

The workflow typically looks like this:
1. Click `check` for checking the annotation (Navbar)
2. `check` will always perform a save at first
3. Now all errors are getting marked (Editor)
4. Fix the error manually or by using a suggestion for correction (Output)
5. Repeat until all errors are fixed

### Resetting 'the tool'
If you want to reload the original files just delete the output folder and restart the tool, otherwise the tool will always refer to the 
saved backup that was created on the first start.