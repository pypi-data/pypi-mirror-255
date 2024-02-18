import sys
from time import sleep
import http.client
from io import BytesIO
import json
from time import sleep
from pathlib import Path
from hashlib import sha256
from enum import Enum
from typing import Optional
from urllib import parse

from tqdm.auto import tqdm
import httpx

from whisper_client.extractAudio import toAudioFolder

# global try_count
# try_count = 0


class Scheme(Enum):
    http = "http"
    https = "https"


class Mode(Enum):
    full = "full"
    text = "text"
    segments = "segments"
    words = "words"


class WhisperClient:

    def __init__(
            self,
            api_key: str,
            *args,
            api_scheme: Scheme = None,
            api_host: str = None,
            api_port: int = None,
            api_url: str = None,
            audio_folder: Path | str = None,
            video_folder: Path | str = None,
            text_folder: Path | str = None,
            erase_previous: bool = True,
            **kwargs
    ) -> None:

        self.last_hash = None
        self.last_status = None
        self.last_launched = None

        self.api_key = api_key

        if not all(e is not None for e in (api_scheme, api_host, api_port)):
            raise NotImplementedError(
                "Please use `api_scheme`, `api_host` and `api_port` for now, `api_url` has not been implemented yet.")

        if not isinstance(api_scheme, Scheme):
            try:
                api_scheme = Scheme(api_scheme)
            except ValueError:
                raise ValueError("api_scheme must be either the string 'http' or 'https' or a Scheme instance.")

        if api_scheme == Scheme.http:
            self.conn = http.client.HTTPConnection(host=api_host, port=api_port, timeout=100)
        elif api_scheme == Scheme.https:
            self.conn = http.client.HTTPSConnection(host=api_host, port=api_port, timeout=100)
        else:
            raise ValueError("bad connexion parameters")

        self.api_url = f"{api_scheme.value}://{api_host}:{api_port}/"
        self.api_scheme = api_scheme
        self.api_host = api_host
        self.api_port = api_port

        if audio_folder is not None:
            if not isinstance(audio_folder, Path):
                audio_folder = Path(audio_folder)
                if not audio_folder.exists():
                    print("ERROR : The audio folder does not exist")
                    audio_folder = None

        if video_folder is not None:
            if not isinstance(video_folder, Path):
                video_folder = Path(video_folder)
                if not video_folder.exists():
                    print("ERROR : The video folder does not exist")
                    video_folder = None

        if ((audio_folder is None) and (video_folder is None)) or (
                (audio_folder is not None) and (video_folder is not None)):
            # print("ERROR : You must specify either an audio folder or a video folder")
            # sys.exit(1)
            pass

        if text_folder is not None:
            if not isinstance(text_folder, Path):
                text_folder = Path(text_folder)
                if not text_folder.exists():
                    print("WARNING : The text folder does not exist")
                    text_folder.mkdir(parents=True)

        else:
            text_folder = Path("text")
            print(f"WARNING : No text folder specified, defaulting to {text_folder.resolve()}")

        if audio_folder is not None:
            self.audio_folder = audio_folder

        if video_folder is not None:
            self.video_folder = video_folder

        self.text_folder = text_folder
        self.erase_previous = erase_previous

        self.headers = {
            # "Content-Type": "audio/wav",
            "X-API-Key": parse.quote(self.api_key),
        }

    def __del__(self) -> None:
        if getattr(self, "conn", None) is None:
            return

        self.conn.close()

    @classmethod
    def from_credentials(cls, json_credentials) -> "WhisperClient":
        with open(json_credentials, "r") as f:
            credentials = json.load(f)
        return cls(**credentials)

    def make_request(
            self,
            method: str,
            path: str,
            data: bytes = None,
            headers: dict = None,
            no_verify: bool = False,
    ) -> Optional[dict]:
        global try_count
        if headers is None:
            headers = self.headers

        self.conn.request(method, path, headers=headers, body=data)

        try:
            res = self.conn.getresponse()
        except http.client.RemoteDisconnected:
            print("WARNING : RemoteDisconnected, retrying")
            try_count += 1
            if try_count < 10:
                return self.make_request(method, path, data, headers, no_verify=no_verify)
            else:
                print("ERROR : Too many retries, aborting")
                return
        data = res.read()
        try:
            data = json.loads(data)
            assert not "error" in data, f"Error in response (error = {data['error']})"
        except json.decoder.JSONDecodeError:
            print("WARNING : Could not decode JSON response")
            return
        except AssertionError as e:
            print(e)
            print("HINT : Check your API key")
            return

        return data

    def get_status(self, hash_audio: str = None, no_verify: bool = False) -> dict:
        if hash_audio is None:
            hash_audio = self.last_hash
        data = self.make_request("GET", f"/status/{hash_audio}", no_verify=no_verify)
        return data

    def get_any_result(self, suffix: str, hash_audio: str = None, no_verify: bool = False) -> \
            Optional[dict | list | str]:
        if hash_audio is None:
            hash_audio = self.last_hash

        data = self.make_request("GET", f"/result/{hash_audio}{suffix}", no_verify=no_verify)

        if data is None or data["status"] != "done":
            print(f"WARNING : No result found for {hash_audio}{suffix}")
            return

        return data["result"]

    def get_result(self, hash_audio: str = None) -> dict:
        return self.get_any_result("", hash_audio)

    def get_result_text(self, hash_audio: str = None) -> str:
        return self.get_any_result("/text", hash_audio)

    def get_result_segments(self, hash_audio: str = None) -> list:
        return self.get_any_result("/segments", hash_audio)

    def get_result_words(self, hash_audio: str = None) -> list:
        return self.get_any_result("/words", hash_audio)

    def send_audio(
            self,
            audio: Path | str,
            hash_audio: str = None,
            no_skip: bool = False,
            no_verify: bool = False,
            verbless: bool = False
    ) -> Optional[dict]:
        if isinstance(audio, str):
            audio = Path(audio)

        if not audio.exists():
            print(f"ERROR : {audio} does not exist")
            return

        with audio.open("rb") as f:
            data = f.read()

        if hash_audio is None:
            hash_audio = self.get_hash_audio(data)

        if not no_skip and self.is_hash_done(hash_audio):
            if verbless:
                print(f"Already done {hash_audio}, skipping")
                return
            print(f"Result for {audio} already exists")
            # return self.get_result(hash_audio)
            return self.get_status(hash_audio, no_verify=no_verify)

        # response = self.make_request("POST", f"/", data=data)
        response = httpx.post(
            self.api_url,
            files={
                "file": (
                    audio.name,
                    data,
                    "audio/wav"
                )
            },
            headers=self.headers,
            timeout=100,
            verify=not no_verify,
        )

        try:
            response = response.json()
            assert "error" not in response, f"Error in response (error = {response['error']})"
        except json.decoder.JSONDecodeError:
            print("WARNING : Could not decode JSON response")
            return
        except AssertionError as e:
            print(e)
            print("HINT : Check your API key")
            return

        if hash_audio != response["hash"]:
            print(f"WARNING : Hash mismatch ({hash_audio} != {response['hash']})")

        self.last_hash = response["hash"]
        self.last_status = response["status"]
        self.last_launched = response["launched"]

        if response["launched"]:
            print(f"Launched {hash_audio}")

        elif response["status"] == "done":
            print(f"Already done {hash_audio}")

        elif response["status"] == "processing":
            print(f"Already processing {hash_audio}")

        else:
            raise ValueError(f"Unknown status {response['status']}")

        return response

    def wait_for_result(self, hash_audio: str = None, interval: int = 30, no_verify: bool = False) -> dict:
        if hash_audio is None:
            hash_audio = self.last_hash

        failed = 0
        while True:
            try:
                status = self.get_status(hash_audio, no_verify=no_verify)
                failed = 0
            except:
                failed += 1
                if failed > 10:
                    raise
                sleep(interval // 10)
                continue
            if status["status"] == "done":
                break
            sleep(interval)

        return status

    def get_result_with_mode(self, hash_audio: str = None, interval: int = 30,
                             mode: Mode = Mode.full) -> dict | str | list:
        if hash_audio is None:
            hash_audio = self.last_hash

        if not isinstance(mode, Mode):
            try:
                mode = Mode(mode)
            except ValueError:
                raise ValueError(
                    "mode must be either the string 'full', 'text', 'segments' or 'words' or directly a Mode instance.")

        match mode:
            case Mode.full:
                return self.get_result(hash_audio)
            case Mode.text:
                return self.get_result_text(hash_audio)
            case Mode.segments:
                return self.get_result_segments(hash_audio)
            case Mode.words:
                return self.get_result_words(hash_audio)
            case _:
                raise ValueError("mode must be either 'full', 'text', 'segments' or 'words'")

    def save_result_with_mode(self, hash_audio: str = None, interval: int = 30, mode: Mode = Mode.full,
                              path: Path | str = None) -> dict | str | list:
        if not isinstance(mode, Mode):
            try:
                mode = Mode(mode)
            except ValueError:
                raise ValueError(
                    "mode must be either the string 'full', 'text', 'segments' or 'words' or directly a Mode instance.")

        result = self.get_result_with_mode(hash_audio=hash_audio, interval=interval, mode=mode)

        if path is None:
            path = self.text_folder / mode.value
            path.mkdir(parents=True, exist_ok=True)

        elif isinstance(path, str):
            if path.endswith(".json"):
                path = self.text_folder / mode.value / path
            path = Path(path)

        elif not isinstance(path, Path):
            raise ValueError("`path` must be either a Path instance or a string")

        if path.is_dir():
            path = path / f"{hash_audio}.json"

        if path.exists():
            if self.erase_previous:
                print(f"WARNING : {path} already exists, erasing")
            else:
                print(f"ERROR : {path} already exists and erase_previous is False, skipping")
                return result

        with path.open("w", encoding="utf-8") as f:
            if not isinstance(result, str):
                json.dump(result, f)
            else:
                f.write(result)

        return result

    def manage_audio_folder(
            self,
            folder: Path | str = None,
            mode: list[Mode] | Mode = Mode.full,
                            interval: int = 30,
            no_skip: bool = False,
            no_verify: bool = False,
    ) -> None:
        if isinstance(mode, list):
            for m in mode:
                self.manage_audio_folder(folder, mode=m, interval=interval, no_skip=no_skip, no_verify=no_verify)
                return

        if isinstance(folder, str):
            folder = Path(folder)

        if folder is None:
            folder = self.audio_folder

        if not folder.exists():
            print(f"ERROR : {folder} does not exist")
            return

        if not folder.is_dir():
            print(f"ERROR : {folder} is not a directory")
            return

        # to_process = list(folder.glob("*.[wmoaf][apgc4l][v3gca]?"))
        to_process = list(folder.glob("*.wav")) + list(folder.glob("*.mp3")) + list(folder.glob("*.ogg")) + list(
            folder.glob("*.flac")) + list(folder.glob("*.m4a"))

        if not to_process:
            print(f"No file to process in {folder}")
            return

        pbar = tqdm(total=len(to_process))

        hashes_n_paths = {}

        for audio in to_process:
            hashes_n_paths.update({
                self.send_audio(audio, no_skip=no_skip, no_verify=no_verify)["hash"]: audio
            })

        while True:
            if not any(hashes_n_paths):
                break

            to_remove = None
            for hash_audio, audio in hashes_n_paths.items():
                if self.is_hash_done(hash_audio, no_verify=no_verify):
                    path = audio.stem + ".json"
                    self.save_result_with_mode(hash_audio, mode=mode, interval=interval, path=path)
                    to_remove = hash_audio
                    pbar.update(1)
                    break
            else:
                # Sleep if no result was found
                sleep(interval)

            del hashes_n_paths[to_remove]

        pbar.close()
        return

    def manage_video_folder(
            self,
            folder: Path | str = None,
            mode: list[Mode] | Mode = Mode.full,
            interval: int = 30,
            no_skip: bool = False,
            no_verify: bool = False,
    ) -> None:
        if isinstance(folder, str):
            folder = Path(folder)

        if folder is None:
            folder = self.video_folder

        if not folder.exists():
            print(f"ERROR : {folder} does not exist")
            return

        if not folder.is_dir():
            print(f"ERROR : {folder} is not a directory")
            return

        to_process = list(folder.glob("*.mp4"))

        if not to_process:
            print(f"No file to process in {folder}")
            return

        audio_folder = self.video_to_audio_folder(folder)

        self.manage_audio_folder(audio_folder, mode=mode, interval=interval, no_skip=no_skip, no_verify=no_verify)

        return

    def video_to_audio_folder(self, folder: Path | str) -> Path:
        if isinstance(folder, str):
            folder = Path(folder)

        if not folder.exists():
            print(f"ERROR : {folder} does not exist")
            return

        if not folder.is_dir():
            print(f"ERROR : {folder} is not a directory")
            return

        audio_folder = folder / "extracted_audio"

        toAudioFolder(folder, audio_folder)

        sleep(1)

        return audio_folder

    def get_hash_audio(self, audio: bytes | BytesIO | Path | str = None) -> str:
        if audio is None:
            if self.last_hash:
                return self.last_hash

            else:
                raise ValueError("No audio passed when no previous hash was computed")

        if isinstance(audio, str):
            audio = Path(audio)

        if isinstance(audio, Path):
            with audio.open("rb") as f:
                audio = f.read()

        if isinstance(audio, BytesIO):
            audio = audio.getvalue()

        return sha256(audio).hexdigest()

    def is_hash_done(self, hash_audio: str = None, no_verify: bool = False) -> bool:
        if hash_audio is None:
            hash_audio = self.last_hash

        status = self.get_status(hash_audio, no_verify=no_verify)

        return status["status"] == "done"


if __name__ == "__main__":
    print(Path.cwd())
    if Path.cwd().name == "whisper_client":
        if Path.parent == "whisper_client":
            root = Path.cwd().parent
        else:
            root = Path.cwd()
    else:
        raise Exception("You must run this script from the whisperClient folder or it's origin folder")

    data = root / "data"
    res = root / "results"
    # wc = WhisperClient.from_credentials(root / "credentials_tunnel.json")
    wc = WhisperClient.from_credentials("/home/marceau/PycharmProjects/whisper-client/credentials.json")

    wc.send_audio("7206340881052372229.wav")

    wc.wait_for_result()

    with open(res / f"{wc.last_hash}.json", "w", encoding="utf-8") as f:
        json.dump(wc.get_result(), f)

    with open(res / f"{wc.last_hash}.txt", "w", encoding="utf-8") as f:
        f.write(wc.get_result_text())

    with open(res / f"{wc.last_hash}_segments.json", "w", encoding="utf-8") as f:
        json.dump(wc.get_result_segments(), f)

    with open(res / f"{wc.last_hash}_words.json", "w", encoding="utf-8") as f:
        json.dump(wc.get_result_words(), f)

    print(wc.last_hash)
