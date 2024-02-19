import subprocess


class GitTools:
    def __init__(self):
        """A class which offers git related commands."""
        super().__init__()

    async def pull(self):
        try:
            result = subprocess.run(["git", "pull"], stdout=subprocess.PIPE)
            output = result.stdout.decode("utf-8")
            return output
        except Exception as e:
            return e
