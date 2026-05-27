import csv
import io
from typing import Literal

from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel


def json_or_csv_response(
    results: list[BaseModel], format: Literal["json", "csv"] | None
) -> Response:
    if format == "csv":
        return _csv_response(results)
    return _json_response(results)


def _json_response(results: list[BaseModel]) -> JSONResponse:
    return JSONResponse(content=[r.model_dump(mode="json") for r in results])


def _csv_response(results: list[BaseModel]) -> Response:
    if not results:
        return Response(content="", media_type="text/csv")
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=results[0].__class__.model_fields.keys())
    writer.writeheader()
    for row in results:
        writer.writerow(row.model_dump(mode="json"))
    return Response(content=buffer.getvalue(), media_type="text/csv")
