/* ============================================================================
   DailyAndacht — shared client helpers
   Loads andachten/overview.sqlite in the browser via sql.js (WASM) so both the
   reader and the backlog can resolve sermons from the index without opening
   every JSON file. The reader then fetches the single matching JSON.
   ========================================================================== */
(function (global) {
    "use strict";

    var SQLJS_VERSION = "1.10.3";
    var SQLJS_BASE = "https://cdnjs.cloudflare.com/ajax/libs/sql.js/" + SQLJS_VERSION + "/";
    var DB_PATH = "andachten/overview.sqlite";

    var MONTHS_DE = [
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ];
    var WEEKDAYS_DE = [
        "Sonntag", "Montag", "Dienstag", "Mittwoch",
        "Donnerstag", "Freitag", "Samstag"
    ];

    var _dbPromise = null;

    /* Load the sql.js runtime once, on demand. */
    function loadSqlJs() {
        if (global.initSqlJs) return Promise.resolve(global.initSqlJs);
        return new Promise(function (resolve, reject) {
            var s = document.createElement("script");
            s.src = SQLJS_BASE + "sql-wasm.js";
            s.onload = function () { resolve(global.initSqlJs); };
            s.onerror = function () { reject(new Error("sql.js konnte nicht geladen werden")); };
            document.head.appendChild(s);
        });
    }

    /* Open the overview database (cached). */
    function openDB() {
        if (_dbPromise) return _dbPromise;
        _dbPromise = Promise.all([
            loadSqlJs().then(function (initSqlJs) {
                return initSqlJs({ locateFile: function (f) { return SQLJS_BASE + f; } });
            }),
            fetch(DB_PATH).then(function (r) {
                if (!r.ok) throw new Error("overview.sqlite nicht gefunden");
                return r.arrayBuffer();
            })
        ]).then(function (parts) {
            var SQL = parts[0];
            return new SQL.Database(new Uint8Array(parts[1]));
        });
        return _dbPromise;
    }

    /* Run a query and return an array of plain row objects. */
    function query(db, sql, params) {
        var stmt = db.prepare(sql);
        if (params) stmt.bind(params);
        var out = [];
        while (stmt.step()) out.push(stmt.getAsObject());
        stmt.free();
        return out;
    }

    /* -- Date helpers ------------------------------------------------------- */

    /* Local YYYY-MM-DD for a Date (avoids UTC off-by-one from toISOString). */
    function isoDate(d) {
        var m = String(d.getMonth() + 1).padStart(2, "0");
        var day = String(d.getDate()).padStart(2, "0");
        return d.getFullYear() + "-" + m + "-" + day;
    }

    /* Parse "YYYY-MM-DD" into a local Date. */
    function parseISO(s) {
        var p = String(s).split("-");
        return new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]));
    }

    /* "18. Juli 2026" */
    function formatDateLong(iso) {
        var d = parseISO(iso);
        return d.getDate() + ". " + MONTHS_DE[d.getMonth()] + " " + d.getFullYear();
    }

    /* "Samstag" */
    function weekday(iso) {
        return WEEKDAYS_DE[parseISO(iso).getDay()];
    }

    /* "Juli 2026" from a "YYYY-MM" key */
    function formatMonth(ym) {
        var p = ym.split("-");
        return MONTHS_DE[Number(p[1]) - 1] + " " + p[0];
    }

    /* -- Domain queries ----------------------------------------------------- */

    /* The sermon to show by default: newest one dated on or before today,
       falling back to the newest overall. */
    function currentId(db) {
        var today = isoDate(new Date());
        var rows = query(db,
            "SELECT id FROM sermons WHERE date <= $t ORDER BY date DESC, created_at DESC LIMIT 1",
            { $t: today });
        if (!rows.length) {
            rows = query(db, "SELECT id FROM sermons ORDER BY date DESC, created_at DESC LIMIT 1");
        }
        return rows.length ? rows[0].id : null;
    }

    function idByDate(db, iso) {
        var rows = query(db,
            "SELECT id FROM sermons WHERE date = $d ORDER BY created_at DESC LIMIT 1",
            { $d: iso });
        return rows.length ? rows[0].id : null;
    }

    function existsId(db, id) {
        return query(db, "SELECT 1 FROM sermons WHERE id = $id LIMIT 1", { $id: id }).length > 0;
    }

    /* Distinct "YYYY-MM" months that contain sermons, ascending. */
    function availableMonths(db) {
        return query(db, "SELECT DISTINCT substr(date,1,7) AS ym FROM sermons ORDER BY ym")
            .map(function (r) { return r.ym; });
    }

    /* All sermons within a "YYYY-MM" month, by day ascending. */
    function sermonsInMonth(db, ym) {
        var start = ym + "-01";
        var p = ym.split("-");
        var next = new Date(Number(p[0]), Number(p[1]), 1); // 1st of following month
        return query(db,
            "SELECT id, date, title, author, read_time_minutes FROM sermons " +
            "WHERE date >= $s AND date < $e ORDER BY date ASC, created_at ASC",
            { $s: start, $e: isoDate(next) });
    }

    /* Every sermon, newest first — small enough to fetch once and filter
       (e.g. for title search) entirely in JS. */
    function allSermons(db) {
        return query(db,
            "SELECT id, date, title, author, read_time_minutes FROM sermons " +
            "ORDER BY date DESC, created_at DESC");
    }

    global.DA = {
        openDB: openDB,
        query: query,
        MONTHS_DE: MONTHS_DE,
        WEEKDAYS_DE: WEEKDAYS_DE,
        isoDate: isoDate,
        parseISO: parseISO,
        formatDateLong: formatDateLong,
        formatMonth: formatMonth,
        weekday: weekday,
        currentId: currentId,
        idByDate: idByDate,
        existsId: existsId,
        availableMonths: availableMonths,
        sermonsInMonth: sermonsInMonth,
        allSermons: allSermons
    };
})(window);
