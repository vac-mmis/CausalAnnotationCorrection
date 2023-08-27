### Domain creation
In addition, the tool can also be used to support the creation of domains. There is an example for this in `examples/creating_domain`.

```
$ acheck check shoes_d_preset.pddl shoes_p1.pddl creating_domain/shoes.csv -l shoes.csv
```

### Resetting 'the tool'
If you want to reload the original files just delete the output folder and restart the tool, otherwise the tool will always refer to the 
saved backup that was created on the first start.