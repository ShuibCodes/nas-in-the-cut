<?php
// Nas In The Cut: the "More of this" signal.
// Counts taps per piece of content. Stores nothing about the visitor.
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo '{"ok":false}';
    exit;
}

$raw = file_get_contents('php://input', false, null, 0, 512);
$data = json_decode($raw, true);
$id = is_array($data) && isset($data['id']) ? (string) $data['id'] : '';

// Only short, simple ids from the site itself are accepted.
if (!preg_match('/^[a-z0-9-]{2,48}$/', $id)) {
    http_response_code(400);
    echo '{"ok":false}';
    exit;
}

$dir = __DIR__ . '/data';
if (!is_dir($dir)) {
    @mkdir($dir, 0750, true);
}
$file = $dir . '/signals.json';
$fp = fopen($file, 'c+');
if (!$fp) {
    http_response_code(500);
    echo '{"ok":false}';
    exit;
}
flock($fp, LOCK_EX);
$counts = json_decode(stream_get_contents($fp) ?: '{}', true);
if (!is_array($counts)) {
    $counts = [];
}
if (!isset($counts[$id]) && count($counts) >= 500) {  // hard cap on distinct ids
    flock($fp, LOCK_UN);
    fclose($fp);
    http_response_code(429);
    echo '{"ok":false}';
    exit;
}
$counts[$id] = (isset($counts[$id]) ? (int) $counts[$id] : 0) + 1;
ftruncate($fp, 0);
rewind($fp);
fwrite($fp, json_encode($counts));
fflush($fp);
flock($fp, LOCK_UN);
fclose($fp);

http_response_code(204);
