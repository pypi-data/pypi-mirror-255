from shutil import which
import subprocess


def prompt(choices=None, header="", multi=False):
    fzf_options = [] 
    if header:
        fzf_options += [f"--header={header}", ]
    if multi:
        fzf_options += [f"--multi", ]


    fzf = FzfPrompt()
    return fzf.prompt(choices, fzf_options=fzf_options)

def prompt_numbered(choices,  *args, transform=None, **kwargs):
    enumerated_choices = []
    for idx, choice in enumerate(choices):
        if transform:
            choice = transform(choice)
        enumerated_choices.append(f"{idx}:{choice}")

    selected = prompt(enumerated_choices)[0]
    idx, _ = selected.split(":")
    return  choices[int(idx)]



FZF_URL = "https://github.com/junegunn/fzf"

class FzfPrompt:
    def __init__(self, executable_path=None):
        if executable_path:
            self.executable_path = executable_path
        elif not which("fzf") and not executable_path:
            raise SystemError(
                f"Cannot find 'fzf' installed on PATH. ({FZF_URL})")
        else:
            self.executable_path = "fzf"

    def prompt(self, choices=None, fzf_options=None, delimiter='\n'):
        if not fzf_options:
            fzf_options = []
        # convert lists to strings [ 1, 2, 3 ] => "1\n2\n3"
        choices_str = delimiter.join(map(str, choices))
        selection = []


        # Invoke fzf externally and write to output file

        pipe = subprocess.run([self.executable_path] + fzf_options, stdout=subprocess.PIPE, input=choices_str, text=True)
        output: str = pipe.stdout

        for line in output.splitlines():
            selection.append(line)


        return selection