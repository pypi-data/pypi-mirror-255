import json
import sys
from pathlib import Path
import argparse

from whisper_client.main import WhisperClient

parser = argparse.ArgumentParser()

parser.add_argument("-k", "--api-key", type=str, help="API key for the whisper API")

parser.add_argument("-s", "--api-scheme", type=str, default="https", help="API scheme for the whisper API")
parser.add_argument("-H", "--api-host", type=str, default="whisper-api.example.com",
                    help="API host for the whisper API")
parser.add_argument("-p", "--api-port", type=int, default=443, help="API port for the whisper API")

parser.add_argument("-u", "--api-url", type=str, default=None, help="API url for the whisper API")

parser.add_argument("-A", "--audio-folder", type=str, default=None,
                    help="Audio folder for the whisper API, allows the client to iterate over the files in the folder and send them to the API"
                    )
parser.add_argument("-V", "--video-folder", type=str, default=None,
                    help="Video folder for the whisper API, allows the client to iterate over the files in the folder and send them to the API"
                    )

parser.add_argument("-T", "--text-folder", type=str, default=None,
                    help="Text folder for the whisper API, if specified, the output text will be saved in this folder"
                    )
parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
parser.add_argument("--no-skip", action="store_true", help="Do not skip already downloaded files")
parser.add_argument("-t", "--timeout", type=int, default=100, help="Timeout for the HTTP connexion")
parser.add_argument("-i", "--interval", type=int, default=30, help="Interval between two status checks")
parser.add_argument("-I", "--input", type=str, default=None, help="Input file to send to the API")
parser.add_argument("-O", "--output", type=str, default=None, help="Output file to save the result")
parser.add_argument("--stdout", action="store_true", help="Print the result to stdout")
parser.add_argument("--stderr", action="store_true", help="Print the result to stderr")
parser.add_argument("--no-verify", action="store_true", help="Do not verify the SSL certificate")
parser.add_argument("-m", "--mode", type=str, default="full",
                    help="Mode for the API, can be 'full', 'text', 'segments' and/or 'words' (comma separated)")
parser.add_argument("-c", "--config", type=str, default=None, help="Config file for the whisper API")


def manage_output(wc: WhisperClient, res: dict, args: argparse.Namespace, mode: str = None, audio_name: str = None):
    if args.output is not None:
        if isinstance(args.output, str):
            output = Path(args.output)
        else:
            raise TypeError(f"args.output must be a str, not a {type(args.output)}")

        if output.is_dir():
            output = output / f"{audio_name}{f'_{mode}' if mode is not None else ''}.json"

    else:

        output = wc.text_folder / f"{audio_name}{f'_{mode}' if mode is not None else ''}.json"

    if output.exists():
        print(f"WARNING : {output} already exists, overwriting")

    with open(output, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)

    if args.stdout:
        print(res)

    if args.stderr:
        print(res, file=sys.stderr)


def cli(parser: argparse.ArgumentParser = parser) -> int:
    args = parser.parse_args()

    config = None

    if args.config is not None:
        config = Path(args.config)
        assert config.exists(), f"ERROR : {config} does not exist"

    else:
        config = Path.cwd() / ".whisperrc"
        if not config.exists():
            config = Path.home() / ".whisperrc"
            if not config.exists():
                config = None

    if config is not None:
        with config.open(mode="r", encoding="utf-8") as f:
            config = json.load(f)

        for k, v in config.items():
            if v is not None and (
                    not hasattr(args, k) # the attribute does not exist
                    or not getattr(args, k) # the attribute is None or False or 0 or ""
                    or getattr(args, k) == parser.get_default(k) # the attribute is the default value
            ):
                setattr(args, k, v)

    if args.verbose:
        print(args)

    if args.api_url is not None:
        api_scheme, api_host, api_port = args.api_url.split("://")[0], args.api_url.split("://")[1].split(":")[0], int(
            args.api_url.split("://")[1].split(":")[1])

    else:
        api_scheme, api_host, api_port = args.api_scheme, args.api_host, args.api_port

    wc = WhisperClient(
        api_key=args.api_key,
        api_scheme=api_scheme,
        api_host=api_host,
        api_port=api_port,
        audio_folder=args.audio_folder,
        video_folder=args.video_folder,
        text_folder=args.text_folder,
    )

    if args.input is not None:
        audiofile = Path(args.input)
        assert audiofile.exists(), f"ERROR : {audiofile} does not exist"

        hash_audio = wc.get_hash_audio(audiofile)

        if not args.no_skip and wc.is_hash_done(hash_audio):
            print(f"Result for {audiofile} already exists, skipping")

        else:
            hash_audio = wc.send_audio(audiofile)["hash"]
            wc.wait_for_result()

        for mode in args.mode.split(","):
            res = wc.get_result_with_mode(mode=mode, hash_audio=hash_audio)

            manage_output(wc, res, args, mode=mode, audio_name=audiofile.name)

    elif args.audio_folder is not None:
        audio_folder = Path(args.audio_folder)
        assert audio_folder.exists(), f"ERROR : {audio_folder} does not exist"

        modes = args.mode.split(",")

        wc.manage_audio_folder(
            folder=audio_folder,
            mode=modes,
            no_skip=args.no_skip,
            interval=args.interval
        )

    elif args.video_folder is not None:
        video_folder = Path(args.video_folder)
        assert video_folder.exists(), f"ERROR : {video_folder} does not exist"

        modes = args.mode.split(",")

        wc.manage_video_folder(
            folder=video_folder,
            mode=modes,
            no_skip=args.no_skip,
            interval=args.interval
        )

    else:
        raise NotImplementedError("You must specify either an audio_folder or a video_folder")

    return 0


if __name__ == "__main__":
    cli(parser)
