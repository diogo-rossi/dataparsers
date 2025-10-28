# Available functions

For a quick reference, below there is a summary for all parameters of the function {py:func}`~dataparsers.arg`, the {py:func}`~dataparsers.dataparser`
decorator and the function {py:func}`~dataparsers.subparser`:

<details>
<summary>Additional parameters for the <code>arg()</code> function:</summary>
<br>

|             Name              |                              Quick description                              |
| :---------------------------: | :-------------------------------------------------------------------------: |
|        [`name_or_flags`](./2_available_functions.md#name-or-flags)        |                A list of option strings, starting with `-`.                 |
|            [`group`](./2_available_functions.md#group)            |          A previously defined `ClassVar` using function {py:func}`~dataparsers.group`           |
|  [`mutually_exclusive_group`](./2_available_functions.md#mutually-exclusive-group)   | A previously defined `ClassVar` using function {py:func}`~dataparsers.mutually_exclusive_group` |
|         [`group_title`](./2_available_functions.md#group-title)         |          The title (or a simple id integer) of the argument group           |
| [`mutually_exclusive_group_id`](./2_available_functions.md#mutually-exclusive-group-id) |       The name (or a simple integer) of the mutually exclusive group        |
|          [`make_flag`](./2_available_functions.md#make-flag)          |              Wether to force the automatic creation of a flag               |

</details>
<br>
<details>
<summary>Parameters of the original <code>add_argument()</code> method used in the <code>arg()</code> function:</summary>
<br>

|    Name    |                            Quick description                            |
| :--------: | :---------------------------------------------------------------------: |
|  [`action`](./2_available_functions.md#action)  |                  The basic type of action to be taken                   |
|  [`nargs`](./2_available_functions.md#nargs)   |      The number of command-line arguments that should be consumed       |
|  [`const`](./2_available_functions.md#const)   |      A constant value required by some action and nargs selections      |
| [`default`](./2_available_functions.md#default)  |   The value produced if the argument is absent from the command line    |
|   [`type`](./2_available_functions.md#type)   |     The type to which the command-line argument should be converted     |
| [`choices`](./2_available_functions.md#choices)  |           A sequence of the allowable values for the argument           |
| [`required`](./2_available_functions.md#required) |          Whether or not the command-line option may be omitted          |
|   [`help`](./2_available_functions.md#help)   |              A brief description of what the argument does              |
| [`metavar`](./2_available_functions.md#metavar)  |               A name for the argument in usage messages.                |
|   [`dest`](./2_available_functions.md#dest)   | The name of the attribute to be added to the object returned (not used) |

</details>
<br>
<details>
<summary>Additional parameters for the <code>dataparser()</code> decorator:</summary>
<br>

|                 Name                 |                  Quick description                  |
| :----------------------------------: | :-------------------------------------------------: |
|        [`groups_descriptions`](./2_available_functions.md#groups-descriptions)         |   A dictionary with argument groups descriptions    |
| [`required_mutually_exclusive_groups`](./2_available_functions.md#required-mutually-exclusive-groups) |             A dictionary with booleans              |
|            [`default_bool`](./2_available_functions.md#default-bool)            | The default boolean value used in in boolean fields |
|           [`help_formatter`](./2_available_functions.md#help-formatter)           |  A formatter function used to format the help text  |

</details>
<br>
<details>
<summary>Parameters of the original <code>ArgumentParser</code> constructor used in the <code>dataparser()</code> decorator:</summary>
<br>

|          Name           |                     Quick description                     |
| :---------------------: | :-------------------------------------------------------: |
|         [`prog`](./2_available_functions.md#prog)          |                  The name of the program                  |
|         [`usage`](./2_available_functions.md#usage)         |          The string describing the program usage          |
|      [`description`](./2_available_functions.md#description)      |         Text to display before the argument help          |
|        [`epilog`](./2_available_functions.md#epilog)         |          Text to display after the argument help          |
|        [`parents`](./2_available_functions.md#parents)        |             A list of ArgumentParser objects              |
|    [`formatter_class`](./2_available_functions.md#formatter-class)    |          A class for customizing the help output          |
|     [`prefix_chars`](./2_available_functions.md#prefix-chars)      |   The set of characters that prefix optional arguments    |
| [`fromfile_prefix_chars`](./2_available_functions.md#fromfile-prefix-chars) |                   The set of characters                   |
|   [`argument_default`](./2_available_functions.md#argument-default)    |          The global default value for arguments           |
|   [`conflict_handler`](./2_available_functions.md#conflict-handler)    |     The strategy for resolving conflicting optionals      |
|       [`add_help`](./2_available_functions.md#add-help)        |          Add a `-h/--help` option to the parser           |
|     [`allow_abbrev`](./2_available_functions.md#allow-abbrev)      |           Allows long options to be abbreviated           |
|     [`exit_on_error`](./2_available_functions.md#exit-on-error)     | Determines whether or not ArgumentParser exits with error |

</details>
<br>
<details>
<summary>Additional parameters for the <code>subparser()</code> function:</summary>
<br>

|    Name    |                     Quick description                      |
| :--------: | :--------------------------------------------------------: |
| [`defaults`](./2_available_functions.md#defaults) | A dictionary with subparser level default attribute values |

</details>
<br>
<details>
<summary>Parameters of the original <code>add_parser()</code> method used in the <code>subparser()</code> function:</summary>
<br>

|   Name    |                                  Quick description                                  |
| :-------: | :---------------------------------------------------------------------------------: |
| [`aliases`](./2_available_functions.md#aliases) | An additional argument which allows multiple strings to refer to the same subparser |
|  [`help`](./2_available_functions.md#help)   |                      A help message for the subparser command                       |

Note: `add_parser()` accepts all kwargs of `ArgumentParser` constructor. It also accepts its own [`help`](./2_available_functions.md#help) and [`aliases`](./2_available_functions.md#aliases)
kwargs.

</details>

---



```{eval-rst}
.. autofunction:: dataparsers.arg
```
---
```{eval-rst}
.. autofunction:: dataparsers.group
```
---
```{eval-rst}
.. autofunction:: dataparsers.mutually_exclusive_group
```
---
```{eval-rst}
.. autofunction:: dataparsers.default
```
---
```{eval-rst}
.. autofunction:: dataparsers.dataparser
```
---
```{eval-rst}
.. autofunction:: dataparsers.parse
```
---
```{eval-rst}
.. autofunction:: dataparsers.parse_known
```
---
```{eval-rst}
.. autofunction:: dataparsers.make_parser
```
---
```{eval-rst}
.. autofunction:: dataparsers.subparser
```
---
```{eval-rst}
.. autofunction:: dataparsers.subparsers
```
---
```{eval-rst}
.. autofunction:: dataparsers.write_help
```
---
