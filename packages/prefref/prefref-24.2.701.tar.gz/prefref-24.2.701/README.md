# PrefRef

### Config init in \_\_main\_\_
#### Subsection
```
example code
```

## Boolean Arguments
There are two types of boolean arguments supported as a Config_Option, the property 'is_flag' will determine how the boolean is handled.

If 'is_flag' is true, the option can only be set by environment variable or console argument and cannot be stored in a config file. Passing the argument or having the environment variable existing, with or without explicitly setting it to a true/false value, will set the Config_Option value to True. Otherwise, the value will be set to the default value of the Config_Option.

If 'is_flag' is false, the option can also be stored in a config file. You can either pass the console argument or have the environment variable set without an explicit statement of true/false to set it to True OR set it explicitly by passing/setting the value to true or false.
