
class ChoiceObj:
    """ Choice class object to store the current state """
    UNCHECKED_VALUE = False
    CHECKED_VALUE = True
    def __init__(self, text):
        # Choice text
        self.text = text
        # Choice states:
        ## selected -> Current choice
        ## checked  -> what the user chose ( [x] )
        self.selected = self.UNCHECKED_VALUE
        self.checked = self.UNCHECKED_VALUE

    def __repr__(self):
        return 'Choice(text={}, checked={}, selected={})'.format(
            self.text, self.checked, self.selected)

    def check(self):
        """ Change check state to TRUE from choice object """
        self.checked = self.CHECKED_VALUE

    def uncheck(self):
        """ Change check state to FALSE from choice object """
        self.checked = self.UNCHECKED_VALUE

    def select(self):
        """ Change selected state to TRUE from choice object """
        self.selected = self.CHECKED_VALUE

    def unselect(self):
        """ Change selected state to FALSE from choice object """
        self.selected = self.UNCHECKED_VALUE

    def invert_check(self):
        """ Invert the check state from choice object """
        self.checked = not self.checked


class ChoiceCrtl:
    """ A class to controll all choice objects """
    def __init__(self, choices):
        # List of choices objects
        self.choices = [ChoiceObj(choice) for choice in choices]

        # Choice currently selected
        self.selected_choice_idx = 0
        self.update_choices()

        self.direction_correlation = self._build_direction_correlation()

    def _build_direction_correlation(self):
        return {
            'up': self._move_selected_choice_to_up,
            'down': self._move_selected_choice_to_down,
            'bottom': self._move_selected_choice_to_bottom,
            'top': self._move_selected_choice_to_top
        }

    def update_choices(self):
        """ Update currently selected choices """
        for idx, choice in enumerate(self.choices):
            if idx == self.selected_choice_idx and not choice.selected:
                choice.select()
            elif choice.selected and idx != self.selected_choice_idx:
                choice.unselect()

    def get_checked_choices(self):
        """Get curretly checked choices

        Returns
        -------
        list of tuple (idx, ChoiceObj)
            List of tuples with index from choice list and ChoiceObj
        """
        return [(idx, choice) for idx, choice in enumerate(self.choices) if choice.checked]

    def get_choiceobj_from_selected_choice(self):
        """Get ChoiceObj from selected choice

        Returns
        -------
        ChoiceObj
            ChoiceObj for selected choice
        """
        return self.choices[self.selected_choice_idx]

    def get_choiceobj_from_next_line(self):
        """Get ChoiceObj from next line choice. If the selected line is the last
                return the first line

        Returns
        -------
        ChoiceObj
            ChoiceObj from next line choice
        """
        if self.selected_choice_idx == len(self.choices) - 1:
            return self.choices[0]
        return self.choices[self.selected_choice_idx + 1]

    def get_choiceobj_from_previous_line(self):
        """Return the Choice Object from previous choice. If the selected line
                is the first return the last line

        Returns
        -------
        ChoiceObj
            ChoiceObj from previous line choice.
        """
        if self.selected_choice_idx == 0:
            return self.choices[-1]
        return self.choices[self.selected_choice_idx - 1]

    def _move_selected_choice_to_bottom(self):
        self.selected_choice_idx = len(self.choices) - 1
        self.update_choices()

    def _move_selected_choice_to_top(self):
        self.selected_choice_idx = 0
        self.update_choices()

    def _move_selected_choice_to_down(self):
        if self.selected_choice_idx < (len(self.choices) - 1):
            self.selected_choice_idx += 1
            self.update_choices()

    def _move_selected_choice_to_up(self):
        if self.selected_choice_idx > 0:
            self.selected_choice_idx -= 1
            self.update_choices()

    def move_selected_choice(self, direction):
        """ Move selected choice to some direction

        Parameters
        ----------
        direction : str
            Direction to move. Possibilites: 
                up: move selected choice to up
                down: move selected choice to down
                top: move selected choice to top
                bottom: move selected choice to bottom
        """
        if direction.lower() in self.direction_correlation:
            self.direction_correlation[direction.lower()]()

    def get_choices_count(self):
        """ Return length of choices objects

        Returns
        -------
        int
            Length of choices objects
        """
        return len(self.choices)

    def yield_items(self):
        """ Yield items from choices objects

        Yields
        ------
        tuple
            Tuple with text, checked and selected
        """
        for choice in self.choices:
            yield choice.text, choice.checked, choice.selected

    def yield_objects(self):
        """ Yield objects from choices objects. This is the same as yield_items
                but return objects instead of tuples.
        Returns
        -------
        tuple
            Tuple with text, checked and selected
        """
        for choice in self.choices:
            yield choice

    def check_or_uncheck_selected_choice(self):
        """ Check or Uncheck the selected choice """
        current_choiceobj = self.get_choiceobj_from_selected_choice()
        current_choiceobj.invert_check()

    def unselected_all(self):
        """ Unselected all choice objects """
        for choice_obj in self.choices:
            choice_obj.unselect()
