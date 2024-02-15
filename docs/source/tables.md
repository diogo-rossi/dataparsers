# Available functions

For a quick reference, below there is a summary for all parameters of the
function `arg()` and the `dataparser()` decorator, which have more than 5
arguments:

- Additional parameters for the `arg()` function:

| `name_or_flags` |          `make_flag`          |
| :-------------: | :---------------------------: |
|  `group_title`  | `mutually_exclusive_group_id` |

- Parameters of the original `add_argument()` method used in the `arg()`
  function:

| `action`  |  `nargs`   | `const` | `default` | `type` |
| :-------: | :--------: | :-----: | :-------: | :----: |
| `choices` | `required` | `help`  | `metavar` | `dest` |

- Additional parameters for the `dataparser()` decorator:

| `groups_descriptions` | `required_mutually_exclusive_groups` |
| :-------------------: | :----------------------------------: |
|    `default_bool`     |              `help_fmt`              |

- Parameters of the original `ArgumentParser` constructor used in the
  `dataparser()` decorator:

|       `prog`       |      `usage`       | `description`  |        `epilog`         |
| :----------------: | :----------------: | :------------: | :---------------------: |
|     `parents`      | `formatter_class`  | `prefix_chars` | `fromfile_prefix_chars` |
| `argument_default` | `conflict_handler` |   `add_help`   |     `allow_abbrev`      |
|  `exit_on_error`   |                    |                |                         |
