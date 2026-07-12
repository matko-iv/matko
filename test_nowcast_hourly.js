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
             nowcastImminentCode, escalateCloud, cloudToCode, HOUR_COVER_MIN,
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

    // 5b. The HOUR_COVER_MIN boundary — the real JSON routinely sits right around it.
    const bDry29 = { hour: '2026-07-09T14:00:00Z', mm: 0, covered_min: 29, peak_point_mmh: 0, peak_disc_mmh: 0 };
    const bDry30 = { hour: '2026-07-09T14:00:00Z', mm: 0, covered_min: 30, peak_point_mmh: 0, peak_disc_mmh: 0 };
    eq(api.gateWeatherCode(61, 80, bDry29, false, null), 61, 'covered 29 min keeps the model rain code');
    eq(api.gateWeatherCode(61, 80, bDry30, false, null), 3, 'covered 30 min strips it (>= HOUR_COVER_MIN)');
    eq(api.nowcastCellMm(bDry29, false), null, 'covered 29 min does not override mm');
    eq(api.nowcastCellMm(bDry30, false), 0, 'covered 30 min overrides mm');

    // 5c. Old-schema bucket (fresh JSON, generator not yet redeployed): mm/covered_min but
    // no peaks. Absent peaks are NOT 0 — such a bucket may neither strip the icon nor
    // restate the mm, or the cell would show a cloudy icon next to a blue 6.0mm.
    const bOld = { hour: '2026-07-09T14:00:00Z', mm: 6.0, covered_min: 60 };
    eq(api.gateWeatherCode(63, 80, bOld, false, null), 63, 'bucket without peaks does not strip the model rain code');
    eq(api.gateWeatherCode(0, 80, bOld, false, null), 0, 'bucket without peaks does not upgrade either');
    eq(api.nowcastCellMm(bOld, false), null, 'bucket without peaks leaves the NWP mm -> icon and mm agree');
    eq(api.nowcastCellMm(bOld, true), null, 'same for the current hour');

    // 6. Beyond the horizon: no bucket, nothing changes.
    eq(api.nowcastHour(ns, '2026-07-09T18:00:00'), null, '18:00 local cell is beyond the horizon');
    eq(api.gateWeatherCode(61, 80, null, false, null), 61, 'no bucket -> code unchanged');
    eq(api.nowcastCellMm(null, false), null, 'no bucket -> mm unchanged');

    // 6b. A status file with no hourly_mm at all (or an empty one) must not throw.
    const nsNoHourly = { ok: true, base_epoch_ms: BASE, series };
    eq(api.nowcastHour(nsNoHourly, '2026-07-09T15:00:00'), null, 'missing hourly_mm -> no bucket');
    eq(api.nowcastHour({ ok: true, base_epoch_ms: BASE, hourly_mm: [] }, '2026-07-09T15:00:00'), null, 'empty hourly_mm -> no bucket');
    eq(api.nowcastHour(ns, ''), null, 'cell with no datetime -> no bucket');
    api.setState(nsNoHourly, null);
    eq(api.gateWeatherCode(61, 80, api.nowcastHour(nsNoHourly, '2026-07-09T15:00:00'), true, null), 61,
       'missing hourly_mm -> clean fall-through, code unchanged');
    api.setState(ns, null);

    // 7. nowcastImminentCode peaks over the 0-60 min window, exclusive of lead 0.
    // (Lead 0 is the base frame; ns.now is the current-state channel for that.)
    const nsImm = {
        ok: true, base_epoch_ms: BASE,
        now: { point_mmh: 0.0 },
        series: [
            { lead_min: 0, point_mmh: 30.0 },   // would be 95 if lead 0 leaked in
            { lead_min: 30, point_mmh: 6.0 },   // -> 63
            { lead_min: 80, point_mmh: 40.0 },  // beyond 60 min, ignored
        ],
    };
    api.setState(nsImm, null);
    eq(api.nowcastImminentCode(), 63, 'imminent code peaks leads 1-60 only (6 mm/h -> 63)');
    nsImm.now = { point_mmh: 25.0 };
    eq(api.nowcastImminentCode(), 95, 'imminent code still takes the now frame into account');
    api.setState(ns, null);

    // SKALA RAIN fallback stays current-hour only, and only when the nowcast is absent.
    api.setState(null, null);
    const rs = { ok: true, ageMin: 5, rainAtLocation: true, bestRain: { dbz: 40 } };
    eq(api.gateWeatherCode(0, 10, null, true, rs), 63, 'no nowcast: SKALA RAIN gates the current hour');
    eq(api.gateWeatherCode(0, 10, null, false, rs), 0, 'no nowcast: SKALA RAIN does not gate later hours');
});

// 8. Stale nowcast (base older than 90 min) -> no nowcast gating at all.
at(BASE + 120 * 60000, () => {
    api.setState(ns, null);
    eq(api.nowcastFresh(ns), false, 'base 120 min old is stale');
    const b = api.nowcastHour(ns, '2026-07-09T16:00:00');
    eq(api.gateWeatherCode(0, 10, b, false, null), 0, 'stale nowcast does not upgrade the icon');
    eq(api.nowcastCellMm(b, false), null, 'stale nowcast does not override mm');
});

// 9. Winter (CET = UTC+1). Everything above is CEST (UTC+2), so a join that just added
// a fixed +2 would pass it — this is the case that pins the epoch join as DST-safe.
const W_BASE = Date.parse('2026-01-15T13:40:00Z');
const nsW = {
    ok: true, base_epoch_ms: W_BASE, horizon_min: 80, timestep_min: 5,
    now: { point_mmh: 0.0, disc_max_mmh: 0.0 }, series: [],
    hourly_mm: [
        { hour: '2026-01-15T13:00:00Z', mm: 0.0, covered_min: 20, peak_point_mmh: 0.0, peak_disc_mmh: 0.0 },
        { hour: '2026-01-15T14:00:00Z', mm: 4.0, covered_min: 60, peak_point_mmh: 5.0, peak_disc_mmh: 6.0 },
    ],
};
at(W_BASE + 5 * 60000, () => {
    api.setState(nsW, null);
    eq(new Date('2026-01-15T14:00:00Z').getHours(), 15, 'TZ check: 14:00Z is 15:00 local (CET, +1)');

    const w15 = api.nowcastHour(nsW, '2026-01-15T15:00:00');
    eq(w15 && w15.hour, '2026-01-15T14:00:00Z', 'winter: 15:00 local cell -> 14:00Z bucket');
    eq(w15 && w15.mm, 4.0, 'winter: 15:00 cell mm = 4.0');
    eq(api.nowcastCellMm(w15, false), 4.0, 'winter: 15:00 cell mm override = 4.0');
    eq(api.gateWeatherCode(0, 5, w15, false, null), 63, 'winter: 15:00 cell gets the rain icon (5 mm/h -> 63)');

    // With a +2 offset the 14:00Z bucket would land here instead.
    eq(api.nowcastHour(nsW, '2026-01-15T16:00:00'), null, 'winter: 16:00 local cell has no bucket');
    eq(api.gateWeatherCode(0, 5, api.nowcastHour(nsW, '2026-01-15T16:00:00'), false, null), 0,
       'winter: 16:00 cell keeps the model code');

    const w14 = api.nowcastHour(nsW, '2026-01-15T14:00:00');
    eq(w14 && w14.hour, '2026-01-15T13:00:00Z', 'winter: 14:00 local cell -> 13:00Z bucket');
    eq(w14 && w14.mm, 0.0, 'winter: 14:00 cell mm = 0.0');
});

if (failures) { console.error(`\n${failures} test(s) failed`); process.exit(1); }
console.log('\nall tests passed');
