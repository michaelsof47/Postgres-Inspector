# Postgres-Inspector

Postgres-Inspector merupakan MCP yang digunakan bukan hanya dapat isi query dari database anda. Namun, bisa dilakukan dengan export schema dan export .csv untuk isi dari tiap tabel

## How to use MCP
1. Lakukan Pengunduhan di lokal komputer anda
2. Install venv terlebih dahulu dan setelah itu jalankan 'pip install -r requirements.txt'
3. Lakukan integrasi dengan AI Agent Tools anda. Untuk saat ini, dari aku akan berikan tata caranya :
- Antigravity
```
{
  "mcpServers": {
    "postgres-inspector": {
      "args": [ <letak_folder>/server.py"],
      "command": "<letak_folder>/.venv/bin/python"
    }
  }
}
```

3. Buatlah .env pada folder. Untuk panduan, anda bisa mengisi pada bagian ini 'DB_HOST', 'DB_PORT'
'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_SSLMODE'
