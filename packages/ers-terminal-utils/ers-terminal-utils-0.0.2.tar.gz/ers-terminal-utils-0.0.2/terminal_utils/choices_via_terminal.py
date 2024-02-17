""" Module for prompt choices """
import sys
from collections import namedtuple

from .lib.terminal_tools import GetchUnix, KeyboardKeys, ColorPrint
from .lib.choices import ChoiceCrtl


actions_function = {}
def register_action(action_name):
    """Decorator to register actions functions

    Parameters
    ----------
    action_name : str
        Name of action
    """
    def decorator(function):
        actions_function[action_name] = function
        return function

    return decorator


_Action = namedtuple('Action', 'name keys')
class ChoicesViaTerminal:
    """ Class to manage choices via UNIX terminal """
    ONE_CHOICE_MODE = "one_choice"
    MULTIPLE_CHOICES_MODE = "multiple_choices"
    AVAILABLE_MODES = (ONE_CHOICE_MODE, MULTIPLE_CHOICES_MODE)
    def __init__(self, tittle, choices, mode="one_choice", colors=None):
        """
        Parameters
        ----------
        tittle : str
            Tittle of the choices
        choices : list of str
            List of texts for choices
        mode : str, optional
            Choice mode, possibilities: one_choice, multiple_choices, by default
                                                                    "one_choice"
        colors : dict, optional
            A dict with color settings.
                Possibilitys:
                {
                    'tittle': {
                        'color': 'MAGENTA',
                        'underline': True,
                        'bold': True
                    },
                    'selected': {
                        ...
                    },
                    'checked': {
                        ...
                    },
                    'help_message': {
                        ...
                    }
                }, by default {}
        """
        self.tittle = tittle
        self.mode = mode

        self.color_settings = self.get_default_color_settings()
        if colors is None:
            colors = {}
        for key, value in colors.items():
            self.color_settings[key].update(value)

        self._print = ColorPrint()
        self.getch = GetchUnix()
        self.keyboard_keys = KeyboardKeys()
        self.choices_crtl = ChoiceCrtl(choices)

        self.actions = [
            _Action(
                'arrow_down',
                (self.keyboard_keys.ARROW_DOWN, )
            ),
            _Action(
                'arrow_up',
                (self.keyboard_keys.ARROW_UP, )
            ),
            _Action(
                'page_down',
                (self.keyboard_keys.PAGE_DOWN, self.keyboard_keys.END)
            ),
            _Action(
                'page_up',
                (self.keyboard_keys.PAGE_UP, self.keyboard_keys.HOME)
            ),
            _Action(
                'enter',
                (self.keyboard_keys.ENTER, )
            ),
            _Action(
                'quit',
                (self.keyboard_keys.CRTL_C, self.keyboard_keys.KEY_Q,
                 self.keyboard_keys.KEY_Q.upper())
            ),
            _Action(
                'check',
                (self.keyboard_keys.SPACE, )
            )
        ]

    def get_default_color_settings(self,):
        """ Get default color settings

        Returns
        -------
        dict
            Return the default color settings for project
        """
        return {
            'tittle': {
                'color': 'MAGENTA',
                'underline': True,
                'bold': True
            },
            'selected': {
                'color': 'BLUE',
                'underline': True,
                'bold': False
            },
            'checked': {
                'color': 'YELLOW',
                'underline': True,
                'bold': False
            },
            'help_message': {
                'color': 'DEFAULT',
                'underline': True,
                'bold': False
            }
        }

    def _is_multiple_choices(self):
        return self.mode == self.MULTIPLE_CHOICES_MODE

    def print_help_message(self):
        """ Print help message """
        if self._is_multiple_choices():
            msg = 'Use <SPACE> to select one or more choice and <ENTER> to continue'
        else:
            msg = 'Use <ENTER> to select ONE choice to continue'
        self._print(msg, **self.color_settings['help_message'])
        self._print('Crtl+C and <q> to quit\n',
                    **self.color_settings['help_message'])

    def print_title(self):
        """ Print tittle of choices """
        self._print('\t' + self.tittle, **self.color_settings['tittle'])

    def print_choices(self):
        """ Print all choices on terminal """
        for text, checked, selected in self.choices_crtl.yield_items():
            msg = ''
            color_conf = {}
            if selected:
                color_conf.update(self.color_settings['selected'])

            if checked:
                msg += '[X] '
                color_conf['color'] = self.color_settings['checked']['color']
            elif not self._is_multiple_choices() and selected:
                color_conf.update(self.color_settings['checked'])
                msg += '[X] '
            else:
                msg += '[ ] '

            msg += text
            self._print(msg, **color_conf)

    @staticmethod
    def _is_key_pressed(_input, keys):
        for key in keys:
            if _input.endswith(key):
                return True, key
        return False, None

    def get_inputs(self):
        """ Get inputs from keyboard

        Yields
        ------
        tuple
            Tuple with action name, key pressed and action function
        """
        _input = ''
        while True:
            # Get last input
            _input += self.getch()

            for action_obj in self.actions:
                key, local_is_key_pressed = self._is_key_pressed(_input,
                                                                action_obj.keys)
                if local_is_key_pressed:
                    yield action_obj.name, key, actions_function[action_obj.name]

    @staticmethod
    def _delete_previous_lines(number_of_lines):
        for _ in range(number_of_lines):
            sys.stdout.write('\x1b[1A\x1b[2K')

    def _update_terminal(self, first_loop=False, last_loop=False):
        if first_loop:
            self.print_help_message()
            self.print_title()
        else:
            self._delete_previous_lines(self.choices_crtl.get_choices_count())
            if last_loop:
                self.choices_crtl.unselected_all()

        self.print_choices()

    def main(self):
        """Main loop of Terminal via choices

        Returns
        -------
        list
            List of tuple with choice index and choice text of checked choices
        """
        self._update_terminal(first_loop=True)
        for _, _, action_function in self.get_inputs():
            if action_function(self):
                break

            self._update_terminal()

        self._update_terminal(last_loop=True)
        checkeds_choices = self.choices_crtl.get_checked_choices()
        return [(choice[0], choice[1].text) for choice in checkeds_choices]

    ### - Action Functions - ###
    @register_action('arrow_down')
    def move_down(self):
        """ Move selected choice down """
        self.choices_crtl.move_selected_choice('down')

    @register_action('arrow_up')
    def move_up(self):
        """ Move selected choice up """
        self.choices_crtl.move_selected_choice('up')

    @register_action('page_down')
    def move_to_bottom(self):
        """ Move selected choice to bottom """
        self.choices_crtl.move_selected_choice('bottom')

    @register_action('page_up')
    def move_to_top(self):
        """ Move selected choice to top """
        self.choices_crtl.move_selected_choice('top')

    @register_action('enter')
    def finish_function(self):
        """ Finish loop execution

        Returns
        -------
        bool
            True if finish execution, False if not.
            If not, the loop will continue.
            If True, the loop will finish.
            This function will return True and if is not a multiple choices(one_choice) 
                            this function will check the selected choice
        """
        if not self._is_multiple_choices():
            self.choices_crtl.check_or_uncheck_selected_choice()
        return True

    @register_action('check')
    def check_function(self):
        """ Check or uncheck selected choice """
        if self._is_multiple_choices():
            self.choices_crtl.check_or_uncheck_selected_choice()

    @register_action('quit')
    def interrupt_execution(self):
        """ Interrupt execution (quit) """
        count = 0
        res = ''
        while res.lower() not in ['y', 'n']:
            count += 1
            if sys.version_info.major < 3:
                # Python2 Logic
                ## Disable pylint and pylance error:
                ### pylint: disable=E0602
                res = raw_input('\nDo you really want to exit? y/n\n') # type: ignore
                # pylint: enable=E0602
            else:
                res = input('\nDo you really want to exit? y/n\n')

        if res.lower() == 'y':
            sys.exit(0)

        self._delete_previous_lines(3 * count)
        return False


if __name__ == '__main__':
    ## Examples 1 - Gender select (one choice only) ##
    TITTLE = 'Please, select your gender:'
    CHOICES = [
        'Feminine',
        'Masculine',
        'Other'
    ]
    result = ChoicesViaTerminal(TITTLE, CHOICES).main()
    index, txt = result[0]

    print('\n\tChosen gender(1): {}\n'.format(CHOICES[index]))

    ## Examples 2 - Gender select with another tittle color (one choice only) ##
    COLORS_SETTINGS = {
        'tittle': {
            'color': 'RED'
        }
    }
    result = ChoicesViaTerminal(TITTLE, CHOICES, colors=COLORS_SETTINGS).main()
    index, txt = result[0]
    print('##\n\tChosen gender(2): {}\n##'.format(CHOICES[index]))

    ## Examples 3 - Choose files to read with another selected color and     ##
    ##                                          BOLD=True (Multiple choices) ##
    COLORS_SETTINGS = {
        'selected': {
            'color': 'DEFAULT',
            'bold': True
        }
    }
    TITTLE = 'Choose files to read:'
    CHOICES = [
        'file1.txt',
        'file2.txt',
        'file3.txt',
        'file4.txt',
        'file5.txt',
    ]
    result = ChoicesViaTerminal(TITTLE, CHOICES, mode='multiple_choices',
                                colors=COLORS_SETTINGS).main()
    print('\n\tChosen files: {}\n'.format([i[1] for i in result]))
