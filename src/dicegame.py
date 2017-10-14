from kivy.app import App
import random


class DiceGame:

    def __init__(self):
        self.die_types = {
            'default': Dice(),
            'fate': FateDice()
        }

    def process_input(self, cmd):
        roll_result = self.process_roll(cmd)
        con = App.get_running_app().get_user_handler().get_connection_manager()
        con.send_roll_to_all(roll_result)

    def process_roll(self, cmd):
        no_of_dice = cmd['no_of_dice']
        die_type = cmd['die_type']
        mod = cmd['mod']
        if mod:
            mod = mod.replace(' ', '')
            mod_op = mod[0]
            mod = int(mod[1:])
        else:
            mod = 0
            mod_op = "+"
        result = None
        if not no_of_dice:
            no_of_dice = 1
        else:
            no_of_dice = int(no_of_dice)
            if no_of_dice < 1:
                no_of_dice = 1

        type_class = None
        if self.type_is_default(die_type):
            type_class = self.die_types['default']
        elif self.type_is_fate(die_type):
            type_class = self.die_types['fate']
        if type_class is None:
            return None
        result = type_class.calculate_and_format(die_type, no_of_dice, mod_op, mod)
        return result

    def type_is_default(self, die_type):
        return die_type[1:].isdigit()

    def type_is_fate(self, die_type):
        return die_type[1:].lower() == 'f'


class Dice:

    def calculate_and_format(self, die_type, no_of_dice, mod_op, mod):
        result = self.calculate(die_type, no_of_dice, mod_op, mod)
        formatted_result = self.format(result)
        return formatted_result

    def calculate(self, die_type, no_of_dice, mod_op, mod):
        die_range = int(die_type[1:])
        if die_range == 0:
            return [0], mod_op, mod, 0
        value = 0
        rolls = []
        for i in range(no_of_dice):
            roll = random.randint(1, die_range)
            value += roll
            rolls.append(roll)

        if mod_op == "+":
            value += mod
        else:
            value -= mod
        return rolls, mod_op, mod, value

    def format(self, result):
        rolls, mod_op, mod, value = result
        rolls = map(str, rolls)
        rolls = ", ".join(rolls)
        msg = "({}) {} {} = {}".format(rolls, mod_op, mod, value)
        return msg


class FateDice(Dice):

    def calculate(self, die_type, no_of_dice, mod_op, mod):
        kinds = ['+', '-', '0']
        rolls = []
        value = 0
        for i in range(no_of_dice):
            kind = random.choice(kinds)
            rolls.append(kind)
        for k in rolls:
            if k == '+':
                value += 1
            elif k == '-':
                value -= 1

        if mod_op == "+":
            value += mod
        else:
            value -= mod
        return rolls, mod_op, mod, value

    def format(self, result):
        rolls, mod_op, mod, value = result
        rolls = ", ".join(rolls)
        msg = "({}) {} {} = {}".format(rolls, mod_op, mod, value)
        return msg


dice_game = DiceGame()
