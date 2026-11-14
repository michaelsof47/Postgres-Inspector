from contextlib import closing
import os
import csv
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from psycopg2 import sql, connect
from psycopg2.extensions import make_dsn
from mcp.server.mcpserver import MCPServer
from psycopg2.extras import RealDictCursor


mcp = MCPServer("database-inspector")

load_dotenv(Path(__file__).parent / ".env")

def build_dsn() -> str:
    return make_dsn(
        host = os.getenv("DB_HOST"),
        port = os.getenv("DB_PORT"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        dbname = os.getenv("DB_NAME"),
        sslmode = os.getenv("DB_SSLMODE", "prefer")
    )

def run_query(query: str | sql.Composable, limit: int = 100, params=None):
    with closing(connect(build_dsn())) as conn:
        conn.set_session(readonly=True)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchmany(limit)]


@mcp.tool()
def query(table_name: str, limit: int = 50) -> list[dict]:
    """Jalankan SELECT (read-only). Maksimal 75 baris."""
    query_str = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
    return run_query(query_str, limit=min(limit, 75))

@mcp.tool()
def export_into_csv(table_name: str, file_path: str = "", limit: int = 100) -> str:
    query_str = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
    rows = run_query(query_str, limit=limit)

    # find a path to write csv into a folder
    if not rows:
        return f"Tabel {table_name} kosong atau tidak tersedia"

    target_path = ""

    if not file_path:
        target_path = Path.cwd() / f"{table_name}.csv"
    else:
        target_path = Path(file_path).expanduser().resolve()

    target_path.parent.mkdir(parents=True, exist_ok=True)

    # write data into file
    filednames = list(rows[0].keys())
    with open(target_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=filednames)
        writer.writeheader()
        writer.writerows(rows)

    return f"Data dari tabel {table_name} berhasil dibuat di {target_path}"

@mcp.tool()
def export_schema(schema: str = "public", file_path: str | None = None):
    target = (
        Path(file_path).expanduser().resolve()
        if file_path
        else Path.cwd() / f"{schema}_dump.sql"                
    )

    command = [
        "pg_dump",
        "--no-owner",
        "--no-privileges",
        "-n", schema,
        "-f", str(target)
    ]

    command.append(build_dsn())

    proc = subprocess.run(command, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)

    return f"Schema '{schema}' berhasil diekspor ke {target}"


if __name__ == "__main__":
    mcp.run()
