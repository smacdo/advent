from donner.annotations import solver, part_one_example, part_two_example
from donner.solution import AbstractSolver
from advent.utils import find_digits, first_and_last


@solver(day=1, year=2023, name="Trebuchet?!")
@part_one_example(
    input=["1abc2", "pqr3stu8vwx", "a1b2c3d4e5f", "treb7uchet"], output="142"
)
@part_two_example(
    input=[
        "two1nine",
        "eightwothree",
        "abcone2threexyz",
        "xtwone3four",
        "4nineeightseven2",
        "zoneight234",
        "7pqrstsixteen",
    ],
    output="281",
)
class Day1Solver(AbstractSolver):
    def part_one(self, input: str) -> int | str | None:
        ### Day 1 - Star 1 #############################################################
        # Load the input file, and for each line get the first and last digit and
        # concatenate them into a two digit number. Sum all those numbers together for
        # the solution.
        sum = 0

        for line in input.splitlines():
            # filter out any values that are not digits from the line
            digits = find_digits(line)
            first, last = first_and_last(digits)

            # Combine the two digits into a number. Take care that sometimes there
            # isn't a second value which means the first and last digit are the same.
            #
            # This is small trick I picked up in code competitions / interviews. To
            # append digits simply multiply them by 10 for each position you want to
            # shift left by.
            number = first * 10 + last
            sum += number

        return str(sum)

    def part_two(self, input: str) -> int | str | None:
        ### Day 1 - Star 2 #############################################################
        # This is annoying - some of the two digit combinations share the last/first
        # character, eg `oneight` -> `18` rather than `oneeight`.
        #
        # There are a few way of solving this. The proper way would be to walk through
        # the characters, and any time "ONE" shows up add a "1" to the digit queue. In
        # the interests of hackery I was curious if there were simpler ways of doing this.
        #
        # I initially tried replacing values like `one` with `1`, but that ran into
        # problems with values like `oneeight`. Saving the last value didn't quite work
        # (`1e`) in certain edge cases. Saving both the first AND last (`o1e`) worked
        # but it felt like too much of a hack.
        #
        # At this point I went back and coded my initial hunch and it worked great.
        DIGITS = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
        }
        sum = 0

        # Go through each line in the file:
        for line in input.splitlines():
            digits = []

            # Go through each character in the line:
            for i, c in enumerate(line):
                # If this is a digit character then simply append it to the queue
                # of digits for this line. Otherwise check if this is the start of a
                # digit name.
                if c.isdigit():
                    digits.append(int(c))
                else:
                    # Check each digit name for a match.
                    for digit_name, digit_value in DIGITS.items():
                        # Make sure we don't go past the end of the string.
                        if i + len(digit_name) > len(line):
                            continue
                        # Check if this char plus the next couple of chars are equal
                        # to the digit name being checked. If so append the digit
                        # value to the queue.
                        if line[i : i + len(digit_name)] == digit_name:
                            digits.append(digit_value)

            # Grab the first and last digits that were found on the line.
            first, last = first_and_last(iter(digits))

            # Combine the two digits into a number. Take care that sometimes there
            # isn't a second value which means the first and last digit are the same.
            #
            # This is small trick I picked up in code competitions / interviews. To
            # append digits simply multiply them by 10 for each position you want to
            # shift left by.
            number = int(first) * 10 + int(last)
            sum += number

        return str(sum)
