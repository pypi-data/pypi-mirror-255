# terminal-utils

<p align="center">A python package for UNIX terminal utilities</p>

# Menu
- [Getting started](#getting-started)
    - [Instalation](#installationuninstallation)
        - [With public pip repository](#with-public-pip-repository)
        - [Local installation](#local-installation)
    - [Uninstallation](#uninstallation)
    - [Usage](#usage)
        - [Dynamic choices](#dynamic-choices-via-terminal)
            - [Mode: One choice](#mode-one-choice-source-code)
            - [Mode: Multiple choices](#mode-multiple-choices-source-code)
- [LICENSE](#license)


# Getting started
## Installation

### With public pip repository
```shell
pip install ers-terminal-utils
```

## Uninstallation
```shell
pip uninstall ers-terminal-utils
```

## Usage
### Dynamic choices via terminal

#### Mode: one choice [(Source Code)](./examples/one_choice_example_1.py)
```python
from terminal_utils.choices_via_terminal import ChoicesViaTerminal

LIST_OF_CHOICES = [
    'Option 1',
    'Option 2',
    'Option 3',
    'Option 4',
    'Option 5'
]
TITTLE = 'Choose an option'
response = ChoicesViaTerminal(TITTLE, LIST_OF_CHOICES).main()
chosen_option_index, chosen_option_text = response[0]

print()
print('Chosen option index: {}\n'
      'Chosen option text: {}'.format(chosen_option_index, chosen_option_text))
```
<p align="center"><img width="800" src="md_files/example_1.gif" /></p>

#### Mode: Multiple choices [(Source Code)](./examples/multiple_choice_example_1.py)
```python
from terminal_utils.choices_via_terminal import ChoicesViaTerminal

LIST_OF_CHOICES = [
    'Option 1',
    'Option 2',
    'Option 3',
    'Option 4',
    'Option 5'
]
TITTLE = 'Choose one or more options'
response = ChoicesViaTerminal(TITTLE, LIST_OF_CHOICES,
                              mode='multiple_choices').main()

print('')
for chosen_option_index, chosen_option_text in response:
    print(
        '- Chosen option index: {}|Chosen option text: {}'.format(chosen_option_index,
                                                                  chosen_option_text)
    )
```
<p align="center"><img width="800" src="md_files/example_2.gif" /></p>

# LICENSE
<p align=center>This project is licensed under the MIT License - see the <a href="https://opensource.org/licenses/MIT">LICENSE</a> page for details.</p>
<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License MIT">
  </a>
</p>