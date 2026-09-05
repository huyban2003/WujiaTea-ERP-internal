/**
 * Wujia Sheet Bridge — cổng ghi cho AI (dán vào Extensions → Apps Script của sheet).
 * Chạy AS "Người chỉnh sửa" (tài khoản deploy) nên có quyền ghi. Bảo vệ bằng SECRET.
 * Dán nguyên file này, đổi SECRET nếu muốn (phải khớp scripts/ba_spec/sheet_endpoint.json),
 * rồi Deploy → New deployment → Web app → Execute as: Me → Who has access: Anyone → Deploy.
 * Copy Web app URL dán lại cho AI.
 */
const SECRET = '<SHARED_SECRET — điền khi deploy Apps Script, xem docs/03_OAUTH_SHEET_SETUP.md>';
const SPREADSHEET_ID = '1HRiRLAZ9FlErRTLvwMaGhsOlYNPJHdf5AEMPvdLkQNE';

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    if (body.secret !== SECRET) return _json({ error: 'forbidden' });
    const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
    const sheet = _resolve(ss, body.sheet);

    if (body.action === 'setCells') {
      // cells: [{row: <1-based>, col: <1-based>, value: <str>}]
      (body.cells || []).forEach(function (c) {
        sheet.getRange(c.row, c.col).setValue(c.value);
      });
      return _json({ ok: true, n: (body.cells || []).length });
    }
    if (body.action === 'appendRow') {
      sheet.appendRow(body.values || []);
      return _json({ ok: true });
    }
    if (body.action === 'ping') {
      return _json({ ok: true, sheet: sheet.getName() });
    }
    return _json({ error: 'unknown action: ' + body.action });
  } catch (err) {
    return _json({ error: String(err) });
  }
}

function _resolve(ss, name) {
  const sheets = ss.getSheets();
  const n = (name || '').trim().toLowerCase();
  let s = sheets.filter(function (x) { return x.getName() === name; })[0]
       || sheets.filter(function (x) { return x.getName().trim().toLowerCase() === n; })[0]
       || sheets.filter(function (x) { return x.getName().trim().toLowerCase().indexOf(n) >= 0; })[0];
  if (!s) throw new Error('Không tìm thấy tab: ' + name);
  return s;
}

function _json(o) {
  return ContentService.createTextOutput(JSON.stringify(o))
    .setMimeType(ContentService.MimeType.JSON);
}
