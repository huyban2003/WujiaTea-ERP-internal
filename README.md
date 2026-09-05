# wujia-devkit

Hai thứ **không** đi theo repo `WujiaTea-ERP-internal` được, gom về đây để 2 máy pull/push đồng bộ:

- `ba_spec/` — toolchain BA/QA (`issue_queue.py`, `qa_sync.py`, `qa_visual_check.py`, `qa_nightly/`…).
  Repo chính gitignore `scripts/ba_spec/` **có chủ đích**: repo đó là repo server `git pull` xuống,
  toolchain này chạm Google Sheet nên không được lên server.
- `commands/` — slash-command của Claude Code (`/wujia-start`, `/wujia-end-sprint`…), vốn nằm ở
  `~/.claude/commands/`, ngoài mọi repo.

## Cài trên máy mới
```bash
git clone git@github.com:<user>/wujia-devkit.git ~/wujia-devkit
~/wujia-devkit/wire.sh          # symlink vào WujiaTea/scripts/ba_spec + ~/.claude/commands
```
Rồi bê tay 3 file secret vào `~/wujia-devkit/ba_spec/` (đã gitignore, **không** qua git):
`sheet_endpoint.json` (mẫu: `sheet_endpoint.example.json`), `client_secret.json`, `token.json`.

## Nhịp đồng bộ hằng ngày
```bash
cd ~/odoo-dev/WujiaTea && git pull        # source + docs + plan + issue ledger
cd ~/wujia-devkit      && git pull        # toolchain + skill
```
Sửa xong bên nào thì commit + push bên đó; máy kia pull. Không có bước copy tay nào nữa.
