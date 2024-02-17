# Available functions

For a quick reference, below there is a summary for all parameters of the
function {py:func}`~dataparsers.arg` and the {py:func}`~dataparsers.dataparser` decorator, which have more than 5
arguments:

- Additional parameters for the {py:func}`~dataparsers.arg` function:

| [`name_or_flags`](./2_available_functions.md#name-or-flags) |          [`make_flag`](./2_available_functions.md#make-flag)          |
| :-------------: | :---------------------------: |
|  [`group_title`](./2_available_functions.md#group-title)  | [`mutually_exclusive_group_id`](./2_available_functions.md#mutually-exclusive-group-id) |

- Parameters of the original `add_argument()` method used in the {py:func}`~dataparsers.arg`
  function:

| name      |
| :-------: |
| [`action`](./2_available_functions.md#action)  |  
| [`nargs`](./2_available_functions.md#nargs)   | 
| [`const`](./2_available_functions.md#const)   | 
| [`default`](./2_available_functions.md#default) |
| [`type`](./2_available_functions.md#type)    |

| [`choices`](./2_available_functions.md#choices) |
| [`required`](./2_available_functions.md#required)|
| [`help`](./2_available_functions.md#help)    |
| [`metavar`](./2_available_functions.md#metavar) |
| [`dest`](./2_available_functions.md#dest)    |

- Additional parameters for the {py:func}`~dataparsers.dataparser` decorator:

| [`groups_descriptions`](./2_available_functions.md#groups-descriptions) | [`required_mutually_exclusive_groups`](./2_available_functions.md#required-mutually-exclusive-groups) |
| :-------------------: | :----------------------------------: |
|    [`default_bool`](./2_available_functions.md#default-bool)     |              [`help_fmt`](./2_available_functions.md#help-fmt)              |

- Parameters of the original `ArgumentParser` constructor used in the
  {py:func}`~dataparsers.dataparser` decorator:

|       [`prog`](./2_available_functions.md#prog)       |      [`usage`](./2_available_functions.md#usage)       | [`description`](./2_available_functions.md#description)  |        [`epilog`](./2_available_functions.md#epilog)         |
| :----------------: | :----------------: | :------------: | :---------------------: |
|     [`parents`](./2_available_functions.md#parents)      | [`formatter_class`](./2_available_functions.md#formatter-class)  | [`prefix_chars`](./2_available_functions.md#prefix-chars) | [`fromfile_prefix_chars`](./2_available_functions.md#fromfile-prefix-chars) |
| [`argument_default`](./2_available_functions.md#argument-default) | [`conflict_handler`](./2_available_functions.md#conflict-handler) |   [`add_help`](./2_available_functions.md#add-help)   |     [`allow_abbrev`](./2_available_functions.md#allow-abbrev)      |
|  [`exit_on_error`](./2_available_functions.md#exit-on-error)   |                    |                |                         |


```{eval-rst}
.. autofunction:: dataparsers.arg
.. autofunction:: dataparsers.dataparser
.. autofunction:: dataparsers.parse
.. autofunction:: dataparsers.make_parser
.. autofunction:: dataparsers.write_help
```