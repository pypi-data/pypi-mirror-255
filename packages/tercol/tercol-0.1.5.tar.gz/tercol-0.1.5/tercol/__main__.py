if __name__ == "__main__":
    import tercol as t

    for hue in range(360):
        try:
            print(t.hsv(hue, 100, 100, "tercol"), end="\r")
        except KeyboardInterrupt:
            break
    print(t.red("Some red text"))
    print(t.bgred("Some text with a red background"))
    print(t.rainbowtext("Some rainbow text"))
    print(
        t.black("█"),
        t.red("█"),
        t.green("█"),
        t.yellow("█"),
        t.blue("█"),
        t.magenta("█"),
        t.cyan("█"),
        t.white("█"),
        t.gray("█"),
        sep="",
    )
    print(t.italic("Italic text"))
    print(t.bold("Bold text"))
    print(t.underlined("Underlined text"))
    print(t.bold(t.italic("Bold-italic text")))
    print(t.blink("Blinking text"))
    print(t.fadedout("Faded out text"))
    print(t.inverted("Inverted text"))
