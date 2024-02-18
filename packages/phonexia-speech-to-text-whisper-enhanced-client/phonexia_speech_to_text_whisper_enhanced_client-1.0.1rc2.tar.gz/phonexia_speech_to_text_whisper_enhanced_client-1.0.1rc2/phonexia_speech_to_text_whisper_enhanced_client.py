import argparse
import logging
import os
from typing import Iterator, Optional

import grpc
import phonexia.grpc.technologies.speech_to_text_whisper_enhanced.v1.speech_to_text_whisper_enhanced_pb2_grpc as stt_grpc
from phonexia.grpc.common.core_pb2 import Audio
from phonexia.grpc.technologies.speech_to_text_whisper_enhanced.v1.speech_to_text_whisper_enhanced_pb2 import (
    TranscribeConfig,
    TranscribeRequest,
)

CHUNK_SIZE = 32000


def request_iterator(file: str, specified_language: Optional[str]) -> Iterator[TranscribeRequest]:
    with open(file, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            config = TranscribeConfig(language=specified_language)
            yield TranscribeRequest(audio=Audio(content=chunk), config=config)


def transcribe(channel: grpc.Channel, file: str, language: Optional[str]):
    stub = stt_grpc.SpeechToTextStub(channel)
    response = stub.Transcribe(request_iterator(file, language))
    for _response in response:
        for segment in _response.result.one_best.segments:
            print(
                f"[{segment.start_time.ToJsonString()} ->"
                f" {segment.end_time.ToJsonString()} {segment.language}] {segment.text}"
            )
        if _response.HasField("processed_audio_length"):
            print(f"Processed audio length: {_response.processed_audio_length.ToJsonString()}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Speech To Text Whisper Enhanced gRPC client. Transcribes input audio into segments"
            " with timestamps."
        )
    )

    parser.add_argument(
        "-H",
        "--host",
        type=str,
        default="localhost:8080",
        help="Server address, default: localhost:8080",
    )
    parser.add_argument(
        "-l",
        "--log_level",
        type=str,
        default="error",
        choices=["critical", "error", "warning", "info", "debug"],
    )
    parser.add_argument("--use_ssl", action="store_true", help="Use SSL connection")

    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help=(
            "Force transcription to specified language, if not set, language is detected"
            " automatically"
        ),
    )
    parser.add_argument("file", type=str, help="Path to input file")

    args = parser.parse_args()

    logging.basicConfig(
        level=args.log_level.upper(),
        format="[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not os.path.isfile(args.file):
        logging.error(f"no such file {args.file}")
        exit(1)

    try:
        logging.info(f"Connecting to {args.host}")
        if args.use_ssl:
            with grpc.secure_channel(
                target=args.host, credentials=grpc.ssl_channel_credentials()
            ) as channel:
                transcribe(channel, args.file, args.language)
        else:
            with grpc.insecure_channel(target=args.host) as channel:
                transcribe(channel, args.file, args.language)

    except grpc.RpcError:
        logging.exception("RPC failed")
        exit(1)
    except Exception:
        logging.exception("Unknown error")
        exit(1)


if __name__ == "__main__":
    main()
