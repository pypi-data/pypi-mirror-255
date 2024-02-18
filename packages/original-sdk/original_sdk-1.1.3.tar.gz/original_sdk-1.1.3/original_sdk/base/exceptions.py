import json


class OriginalAPIException(Exception):
    def __init__(self, text: str, status_code: int) -> None:
        self.response_text = text
        self.status_code = status_code
        self.json_response = False

        try:
            full_error = json.loads(text)
            self.error_type = full_error["error"]["type"]
            self.error_detail = full_error["error"]["detail"]
            self.json_response = True
        except ValueError:
            pass

    def __str__(self) -> str:
        if self.json_response:
            return f"Original error code {self.status_code}: type: {self.error_type}: {self.error_detail}"
        else:
            return f"Original error HTTP code: {self.status_code}"
