param(
    [string]$Endpoint = "http://127.0.0.1:9222/json/list"
)

$ErrorActionPreference = "Stop"
$targets = @(Invoke-RestMethod $Endpoint)
$page = @($targets | Where-Object { $_.type -eq "page" })[0]
if (-not $page) { throw "Kein WebView-Debugziel gefunden." }

$socket = [System.Net.WebSockets.ClientWebSocket]::new()
$socket.ConnectAsync([Uri]$page.webSocketDebuggerUrl, [Threading.CancellationToken]::None).GetAwaiter().GetResult()

function Send-Cdp([int]$Id, [string]$Method, [hashtable]$Params = @{}) {
    $json = @{ id = $Id; method = $Method; params = $Params } | ConvertTo-Json -Compress -Depth 10
    $bytes = [Text.Encoding]::UTF8.GetBytes($json)
    $segment = [ArraySegment[byte]]::new($bytes)
    $socket.SendAsync($segment, [Net.WebSockets.WebSocketMessageType]::Text, $true, [Threading.CancellationToken]::None).GetAwaiter().GetResult() | Out-Null
}

function Receive-Cdp {
    $buffer = New-Object byte[] 1048576
    $segment = [ArraySegment[byte]]::new($buffer)
    $result = $socket.ReceiveAsync($segment, [Threading.CancellationToken]::None).GetAwaiter().GetResult()
    $length = $result.Count
    while (-not $result.EndOfMessage) {
        $next = [ArraySegment[byte]]::new($buffer, $length, $buffer.Length - $length)
        $result = $socket.ReceiveAsync($next, [Threading.CancellationToken]::None).GetAwaiter().GetResult()
        $length += $result.Count
    }
    return ([Text.Encoding]::UTF8.GetString($buffer, 0, $length) | ConvertFrom-Json)
}

Send-Cdp 1 "Runtime.enable"
Send-Cdp 2 "Log.enable"
Send-Cdp 3 "Page.enable"
Send-Cdp 4 "Page.reload" @{ ignoreCache = $true }

$messages = @()
do {
    $message = Receive-Cdp
    if ($message -and ($message.method -in @("Runtime.exceptionThrown", "Log.entryAdded", "Runtime.consoleAPICalled"))) {
        $messages += $message
    }
} until ($message.method -eq "Page.loadEventFired")

$expression = "JSON.stringify({title:document.title,text:document.body.innerText,html:document.body.innerHTML.slice(0,500),resources:performance.getEntriesByType('resource').map(r=>({name:r.name,status:r.responseStatus,bytes:r.transferSize}))})"
Send-Cdp 5 "Runtime.evaluate" @{ expression = $expression; returnByValue = $true }
do {
    $evaluation = Receive-Cdp
    if ($evaluation -and ($evaluation.method -in @("Runtime.exceptionThrown", "Log.entryAdded", "Runtime.consoleAPICalled"))) {
        $messages += $evaluation
    }
} until ($evaluation.id -eq 5)

[pscustomobject]@{
    Messages = $messages
    Evaluation = if ($evaluation) { $evaluation.result.result.value | ConvertFrom-Json } else { $null }
} | ConvertTo-Json -Depth 20

$socket.CloseAsync([Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "done", [Threading.CancellationToken]::None).GetAwaiter().GetResult()

