"""Generate and persist images with OpenAI's ``gpt-image-2`` model.

The cloud routine should call :func:`generate_image` with a text prompt, a PNG
destination, and an optional supported image size. The function reads
``OPENAI_API_KEY`` exclusively from the process environment, performs up to
three attempts for transient failures, writes the decoded PNG atomically, and
returns a stable result dictionary instead of raising expected API errors::

    {
        "success": bool,
        "path": str | None,
        "error_type": str | None,
        "error_message": str | None,
    }

No third-party packages are required.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import socket
import tempfile
import time
import urllib.error
import urllib.request
from typing import Any


API_URL = "https://api.openai.com/v1/images/generations"
MODEL = "gpt-image-2"
MAX_ATTEMPTS = 3
REQUEST_TIMEOUT_SECONDS = 120
RETRYABLE_ERRORS = {"RATE_LIMIT", "SERVER_ERROR", "NETWORK_ERROR"}


def _result(
    *,
    success: bool,
    path: str | None = None,
    error_type: str | None = None,
    error_message: str | None = None,
) -> dict[str, Any]:
    return {
        "success": success,
        "path": path,
        "error_type": error_type,
        "error_message": error_message,
    }


def _safe_message(value: object, api_key: str) -> str:
    """Convert an error to text while ensuring the credential cannot escape."""
    message = str(value).strip() or "No error details were provided."
    return message.replace(api_key, "[REDACTED]") if api_key else message


def _parse_api_error(raw_body: bytes, api_key: str) -> tuple[str, str | None]:
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "The API returned an unreadable error response.", None

    error = payload.get("error", {}) if isinstance(payload, dict) else {}
    if not isinstance(error, dict):
        return "The API returned an unexpected error response.", None

    message = _safe_message(error.get("message", "OpenAI API request failed."), api_key)
    code = error.get("code")
    return message, code if isinstance(code, str) else None


def _classify_http_error(
    status: int, raw_body: bytes, api_key: str
) -> tuple[str, str]:
    message, api_code = _parse_api_error(raw_body, api_key)
    if status == 401:
        return "AUTH_ERROR", message
    if status == 429:
        if api_code == "credit_balance_exhausted":
            return "INSUFFICIENT_QUOTA", message
        return "RATE_LIMIT", message
    if status == 400:
        return "INVALID_REQUEST", message
    if 500 <= status <= 599:
        return "SERVER_ERROR", message
    return "UNKNOWN", message


def _save_png(image_bytes: bytes, output_path: str) -> None:
    """Atomically replace the destination so failed writes leave no partial PNG."""
    destination = os.path.abspath(os.path.expanduser(output_path))
    directory = os.path.dirname(destination)
    os.makedirs(directory, exist_ok=True)

    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=directory, prefix=".image-", suffix=".png", delete=False
        ) as temporary_file:
            temporary_path = temporary_file.name
            temporary_file.write(image_bytes)
        os.replace(temporary_path, destination)
    except Exception:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass
        raise


def generate_image(
    prompt: str, output_path: str, size: str = "1024x1024"
) -> dict[str, Any]:
    """Generate one PNG and return a stable success/error result dictionary.

    ``OPENAI_API_KEY`` must be present in the environment. Authentication,
    quota, and invalid-request failures return immediately. Rate-limit, server,
    and network failures use exponential backoff and make at most three total
    attempts. Expected API failures are returned rather than raised.
    """
    if not isinstance(prompt, str) or not prompt.strip():
        return _result(
            success=False,
            error_type="INVALID_REQUEST",
            error_message="prompt must be a non-empty string.",
        )
    if not isinstance(output_path, str) or not output_path.strip():
        return _result(
            success=False,
            error_type="INVALID_REQUEST",
            error_message="output_path must be a non-empty string.",
        )
    if not isinstance(size, str) or not size.strip():
        return _result(
            success=False,
            error_type="INVALID_REQUEST",
            error_message="size must be a non-empty string.",
        )

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return _result(
            success=False,
            error_type="AUTH_ERROR",
            error_message="OPENAI_API_KEY is not set in the environment.",
        )

    request_body = json.dumps(
        {"model": MODEL, "prompt": prompt, "size": size, "n": 1}
    ).encode("utf-8")
    last_error = _result(
        success=False,
        error_type="UNKNOWN",
        error_message="Image generation failed.",
    )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        request = urllib.request.Request(
            API_URL,
            data=request_body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=REQUEST_TIMEOUT_SECONDS
            ) as response:
                response_payload = json.loads(response.read().decode("utf-8"))

            encoded_image = response_payload["data"][0]["b64_json"]
            if not isinstance(encoded_image, str) or not encoded_image:
                raise ValueError("API response did not contain image data.")
            image_bytes = base64.b64decode(encoded_image, validate=True)
            _save_png(image_bytes, output_path)
            return _result(success=True, path=output_path)

        except urllib.error.HTTPError as error:
            try:
                raw_body = error.read()
            except Exception:
                raw_body = b""
            error_type, message = _classify_http_error(
                error.code, raw_body, api_key
            )
            last_error = _result(
                success=False, error_type=error_type, error_message=message
            )
        except (urllib.error.URLError, TimeoutError, socket.timeout) as error:
            reason = error.reason if isinstance(error, urllib.error.URLError) else error
            last_error = _result(
                success=False,
                error_type="NETWORK_ERROR",
                error_message=_safe_message(reason, api_key),
            )
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError, IndexError,
                TypeError, ValueError, binascii.Error, OSError) as error:
            return _result(
                success=False,
                error_type="UNKNOWN",
                error_message=_safe_message(error, api_key),
            )
        except Exception as error:  # Preserve the public no-raise error contract.
            return _result(
                success=False,
                error_type="UNKNOWN",
                error_message=_safe_message(error, api_key),
            )

        if last_error["error_type"] not in RETRYABLE_ERRORS:
            return last_error
        if attempt < MAX_ATTEMPTS:
            time.sleep(2 ** (attempt - 1))

    return last_error


def _main() -> int:
    parser = argparse.ArgumentParser(description="Generate a PNG with gpt-image-2.")
    parser.add_argument("prompt", help="Text description of the image to generate")
    parser.add_argument("output_path", help="Where to save the generated PNG")
    parser.add_argument("--size", default="1024x1024", help="Generated image size")
    args = parser.parse_args()

    result = generate_image(args.prompt, args.output_path, args.size)
    if result["success"]:
        print(f"SUCCESS: Image saved to {result['path']}")
        return 0

    print(f"FAILURE [{result['error_type']}]: {result['error_message']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(_main())
