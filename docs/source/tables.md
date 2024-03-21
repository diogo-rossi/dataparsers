# Available functions

For a quick reference, below there is a summary for all parameters of the function `arg()`, the `dataparser()`
decorator and the function `subparser()`:

<details>
<summary>Additional parameters for the <code>arg()</code> function:</summary>
<br>

|             Name              |                              Quick description                              |
| :---------------------------: | :-------------------------------------------------------------------------: |
|        `name_or_flags`        |                A list of option strings, starting with `-`.                 |
|            `group`            |          A previously defined `ClassVar` using function `group()`           |
|  `mutually_exclusive_group`   | A previously defined `ClassVar` using function `mutually_exclusive_group()` |
|         `group_title`         |          The title (or a simple id integer) of the argument group           |
| `mutually_exclusive_group_id` |       The name (or a simple integer) of the mutually exclusive group        |
|          `make_flag`          |              Wether to force the automatic creation of a flag               |

</details>
<br>
<details>
<summary>Parameters of the original <code>add_argument()</code> method used in the <code>arg()</code> function:</summary>
<br>

|    Name    |                            Quick description                            |
| :--------: | :---------------------------------------------------------------------: |
|  `action`  |                  The basic type of action to be taken                   |
|  `nargs`   |      The number of command-line arguments that should be consumed       |
|  `const`   |      A constant value required by some action and nargs selections      |
| `default`  |   The value produced if the argument is absent from the command line    |
|   `type`   |     The type to which the command-line argument should be converted     |
| `choices`  |           A sequence of the allowable values for the argument           |
| `required` |          Whether or not the command-line option may be omitted          |
|   `help`   |              A brief description of what the argument does              |
| `metavar`  |               A name for the argument in usage messages.                |
|   `dest`   | The name of the attribute to be added to the object returned (not used) |

</details>
<br>
<details>
<summary>Additional parameters for the <code>dataparser()</code> decorator:</summary>
<br>

|                 Name                 |                  Quick description                  |
| :----------------------------------: | :-------------------------------------------------: |
|        `groups_descriptions`         |   A dictionary with argument groups descriptions    |
| `required_mutually_exclusive_groups` |             A dictionary with booleans              |
|            `default_bool`            | The default boolean value used in in boolean fields |
|           `help_formatter`           |  A formatter function used to format the help text  |

</details>
<br>
<details>
<summary>Parameters of the original <code>ArgumentParser</code> constructor used in the <code>dataparser()</code> decorator:</summary>
<br>

|          Name           |                     Quick description                     |
| :---------------------: | :-------------------------------------------------------: |
|         `prog`          |                  The name of the program                  |
|         `usage`         |          The string describing the program usage          |
|      `description`      |         Text to display before the argument help          |
|        `epilog`         |          Text to display after the argument help          |
|        `parents`        |             A list of ArgumentParser objects              |
|    `formatter_class`    |          A class for customizing the help output          |
|     `prefix_chars`      |   The set of characters that prefix optional arguments    |
| `fromfile_prefix_chars` |                   The set of characters                   |
|   `argument_default`    |          The global default value for arguments           |
|   `conflict_handler`    |     The strategy for resolving conflicting optionals      |
|       `add_help`        |          Add a `-h/--help` option to the parser           |
|     `allow_abbrev`      |           Allows long options to be abbreviated           |
|     `exit_on_error`     | Determines whether or not ArgumentParser exits with error |

</details>
<br>
<details>
<summary>Additional parameters for the <code>subparser()</code> function:</summary>
<br>

|    Name    |                     Quick description                      |
| :--------: | :--------------------------------------------------------: |
| `defaults` | A dictionary with subparser level default attribute values |

</details>
<br>
<details>
<summary>Parameters of the original <code>add_parser()</code> method used in the <code>subparser()</code> function:</summary>
<br>

|   Name    |                                  Quick description                                  |
| :-------: | :---------------------------------------------------------------------------------: |
| `aliases` | An additional argument which allows multiple strings to refer to the same subparser |
|  `help`   |                      A help message for the subparser command                       |

Note: `add_parser()` accepts all kwargs of `ArgumentParser` constructor. It also accepts its own `help` and `aliases`
kwargs.

</details>

---
