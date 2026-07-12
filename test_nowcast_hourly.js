// Tests the SKALA NOWCAST hourly gating in docs/forecast.html.
// Run:  node test_nowcast_hourly.js      (exit 0 = pass)
//
// The gating functions are inline in forecast.html, so we slice the real source
// out of the file and evaluate it — nothing is copied into this test. The slice
// runs from the marker comment to just before dailyIconKey(); if you move or
// rename either anchor, update MARK_START / MARK_END below.

if (process.env.TZ !== 'Europe/Podgorica') {
    // The UTC-bucket -> local-cell join is timezone-sensitive, and TZ must be set
    // before the first Date use, so re-exec with the page's timezone.
    const r = require('child_process').spawnSync(process.execPath, [__filename], {
        stdio: 'inherit', env: Object.assign({}, process.env, { TZ: 'Europe/Podgorica' })
    });
    process.exit(r.status === null ? 1 : r.status);
}

const fs = require('fs');
const path = require('path');

const MARK_START = '// ---- SKALA gating of near-term rain icons ----';
const MARK_END = 'function dailyIconKey(';

const html = fs.readFileSync(path.join(__dirname, 'docs', 'forecast.html'), 'utf8');
const start = html.indexOf(MARK_START);
const end = html.indexOf(MARK_END, start);
if (start < 0 || end < 0) {
    console.error('FAIL: could not locate the gating region in docs/forecast.html');
    process.exit(1);
}
const src = html.slice(start, end);

const api = new Function(src + `
    return { nowcastHour, nowcastCellMm, gateWeatherCode, nowcastFresh, nowcastIntensityCode,
             escalateCloud, cloudToCode, HOUR_COVER_MIN,
             setState: (ns, rs) => { nowcastState = ns; radarState = rs; } };
`)();

let failures = 0;
function eq(actual, expected, what) {
    const ok = Object.is(actual, expected);
    if (!ok) { failures++; console.error(`FAIL: ${what}\n  expected: ${expected}\n  actual:   ${actual}`); }
    else console.log(`ok: ${what}`);
}

const realNow = Date.now;
function at(epochMs, fn) {
    Date.now = () => epochMs;
    try { fn(); } finally { Date.now = realNow; }
}

// Sanity: the whole join rests on the process running in Budva's timezone.
eq(new Date('2026-07-09T13:00:00Z').getHours(), 15, 'TZ check: 13:00Z is 15:00 local (CEST)');

// Base 13:40Z = 15:40 local. Rain starts at 14:05Z, i.e. entirely inside the
// 14:00Z clock hour (= the 16:00 local cell). The old lead-offset math integrated
// leads 0-60 (13:40Z-14:40Z) into the CURRENT hour's cell, crediting 4.0 mm of the
// 16:00 cell's rain to the 15:00 cell — and its icon with it.
const BASE = Date.parse('2026-07-09T13:40:00Z');
const series = [];
for (let lead = 5; lead <= 80; lead += 5) {
    const wet = lead >= 25;
    series.push({ lead_min: lead, point_mmh: wet ? 6.0 : 0.0, disc_max_mmh: wet ? 8.0 : 0.0 });
}
const ns = {
    ok: true, base_epoch_ms: BASE, horizon_min: 80, timestep_min: 5,
    now: { point_mmh: 0.0, disc_max_mmh: 0.0 },
    series,
    hourly_mm: [
        { hour: '2026-07-09T13:00:00Z', mm: 0.0, covered_min: 20, peak_point_mmh: 0.0, peak_disc_mmh: 0.0 },
        { hour: '2026-07-09T14:00:00Z', mm: 6.0, covered_min: 60, peak_point_mmh: 6.0, peak_disc_mmh: 8.0 },
    ],
};

at(BASE + 5 * 60000, () => {
    api.setState(ns, null);

    // 1. Mid-hour bug: the buckets must land on the right clock-hour cells.
    const cur = api.nowcastHour(ns, '2026-07-09T15:00:00');
    const nxt = api.nowcastHour(ns, '2026-07-09T16:00:00');
    eq(cur && cur.hour, '2026-07-09T13:00:00Z', '15:00 local cell -> 13:00Z bucket');
    eq(nxt && nxt.hour, '2026-07-09T14:00:00Z', '16:00 local cell -> 14:00Z bucket');
    eq(cur && cur.mm, 0.0, '15:00 cell mm = 0.0 (rain is all in the next clock hour)');
    eq(nxt && nxt.mm, 6.0, '16:00 cell mm = 6.0');
    eq(api.nowcastCellMm(cur, true), 0.0, 'current hour overrides mm even at 20 min coverage');
    eq(api.nowcastCellMm(nxt, false), 6.0, 'fully covered hour overrides mm');

    // Same bug, on the icon: the rain icon belongs to the 16:00 cell, not the 15:00 one.
    eq(api.gateWeatherCode(0, 5, cur, true, null), 0, '15:00 cell stays clear (no rain in its hour)');
    eq(api.gateWeatherCode(0, 5, nxt, false, null), 63, '16:00 cell gets the rain icon (6 mm/h -> 63)');

    // 2. Icon upgrade on rain at Budva.
    const b10 = { hour: '2026-07-09T14:00:00Z', mm: 5, covered_min: 60, peak_point_mmh: 10, peak_disc_mmh: 12 };
    eq(api.gateWeatherCode(0, 10, b10, false, null), 82, 'peak_point 10 mm/h upgrades clear -> 82');

    // 3. Never downgrade a heavier model code.
    const bLight = { hour: '2026-07-09T14:00:00Z', mm: 0.3, covered_min: 60, peak_point_mmh: 0.5, peak_disc_mmh: 0.5 };
    eq(api.gateWeatherCode(95, 90, bLight, false, null), 95, 'model 95 + light nowcast rain stays 95');

    // 4. Nearby cell, dry at Budva.
    const bStrong = { hour: '2026-07-09T14:00:00Z', mm: 0, covered_min: 60, peak_point_mmh: 0, peak_disc_mmh: 30 };
    const bWeak = { hour: '2026-07-09T14:00:00Z', mm: 0, covered_min: 60, peak_point_mmh: 0, peak_disc_mmh: 5 };
    eq(api.gateWeatherCode(0, 10, bStrong, false, null), 95, 'strong nearby cell -> 95');
    eq(api.gateWeatherCode(0, 10, bWeak, false, null), api.escalateCloud(0), 'weak nearby cell -> cloud nudge, no rain code');
    eq(api.gateWeatherCode(0, 10, bWeak, false, null), 2, 'weak nearby cell: clear -> partly cloudy');

    // 5. Strip model rain only when the hour is actually covered.
    const bDryCovered = { hour: '2026-07-09T14:00:00Z', mm: 0, covered_min: 60, peak_point_mmh: 0, peak_disc_mmh: 0 };
    const bDryThin = { hour: '2026-07-09T14:00:00Z', mm: 0, covered_min: 10, peak_point_mmh: 0, peak_disc_mmh: 0 };
    eq(api.gateWeatherCode(61, 80, bDryCovered, false, null), api.cloudToCode(80), 'dry + covered 60 min strips model rain');
    eq(api.gateWeatherCode(61, 80, bDryCovered, false, null), 3, 'stripped code is cloudToCode(80) = 3');
    eq(api.gateWeatherCode(61, 80, bDryThin, false, null), 61, 'dry but only 10 min covered keeps the model rain code');
    eq(api.nowcastCellMm(bDryThin, false), null, 'thinly covered non-current hour keeps the NWP mm');

    // 6. Beyond the horizon: no bucket, nothing changes.
    eq(api.nowcastHour(ns, '2026-07-09T18:00:00'), null, '18:00 local cell is beyond the horizon');
    eq(api.gateWeatherCode(61, 80, null, false, null), 61, 'no bucket -> code unchanged');
    eq(api.nowcastCellMm(null, false), null, 'no bucket -> mm unchanged');

    // SKALA RAIN fallback stays current-hour only, and only when the nowcast is absent.
    api.setState(null, null);
    const rs = { ok: true, ageMin: 5, rainAtLocation: true, bestRain: { dbz: 40 } };
    eq(api.gateWeatherCode(0, 10, null, true, rs), 63, 'no nowcast: SKALA RAIN gates the current hour');
    eq(api.gateWeatherCode(0, 10, null, false, rs), 0, 'no nowcast: SKALA RAIN does not gate later hours');
});

// 7. Stale nowcast (base older than 90 min) -> no nowcast gating at all.
at(BASE + 120 * 60000, () => {
    api.setState(ns, null);
    eq(api.nowcastFresh(ns), false, 'base 120 min old is stale');
    const b = api.nowcastHour(ns, '2026-07-09T16:00:00');
    eq(api.gateWeatherCode(0, 10, b, false, null), 0, 'stale nowcast does not upgrade the icon');
    eq(api.nowcastCellMm(b, false), null, 'stale nowcast does not override mm');
});

if (failures) { console.error(`\n${failures} test(s) failed`); process.exit(1); }
console.log('\nall tests passed');
