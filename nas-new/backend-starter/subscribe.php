<?php
// Nas In The Cut: newsletter sign-up relay (starter, ready to finish).
//
// Why a relay: Beehiiv and Kit need a secret API key. A key in the page would be
// public, so the browser posts to this file and this file talks to the provider.
//
// To switch on:
//   1. Fill in nitc-config.php (see nitc-config.sample.php) and upload it above public_html.
//   2. Copy this file to src/php/subscribe.php and add it to the copy list in build.py main()
//      next to signal.php, cup.php and stats.php.
//   3. In build.py set SUBSCRIBE_ENDPOINT = "subscribe.php", run the build and the audit, upload.
//
// The page sends:   POST JSON {"email": "...", "source": "subscribe" | "subscribe-final" | ...}
// This replies:     200 {"ok":true}  or  4xx/5xx {"ok":false}. The page only checks the status.

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex');

function done($code) {
    http_response_code($code);
    echo json_encode(['ok' => $code < 300]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') done(405);

$cfgFile = dirname(__DIR__) . '/nitc-config.php';
$cfg = is_file($cfgFile) ? require $cfgFile : null;
if (!is_array($cfg)) done(503);

$data = json_decode(file_get_contents('php://input', false, null, 0, 2048), true);
$email = is_array($data) ? strtolower(trim((string) ($data['email'] ?? ''))) : '';
$source = is_array($data) ? preg_replace('/[^a-z0-9-]/', '', (string) ($data['source'] ?? 'site')) : 'site';
if (strlen($email) > 120 || !filter_var($email, FILTER_VALIDATE_EMAIL)) done(400);

// Simple flood guard: 10 sign-ups an hour per connection. Only a one way fingerprint is kept.
$dir = __DIR__ . '/data';
if (!is_dir($dir)) @mkdir($dir, 0750, true);
$fp = fopen($dir . '/subscribe-rate.json', 'c+');
if ($fp) {
    flock($fp, LOCK_EX);
    $hits = json_decode(stream_get_contents($fp) ?: '{}', true);
    if (!is_array($hits)) $hits = [];
    $now = time();
    foreach ($hits as $k => $list) {
        $hits[$k] = array_values(array_filter((array) $list, function ($t) use ($now) { return $t > $now - 3600; }));
        if (!$hits[$k]) unset($hits[$k]);
    }
    $who = hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . '|nitc-sub');
    $blocked = count($hits[$who] ?? []) >= 10;
    if (!$blocked) $hits[$who][] = $now;
    ftruncate($fp, 0); rewind($fp); fwrite($fp, json_encode($hits)); fflush($fp);
    flock($fp, LOCK_UN); fclose($fp);
    if ($blocked) done(429);
}

function post_json($url, $headers, $body) {
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_HTTPHEADER => array_merge(['Content-Type: application/json', 'Accept: application/json'], $headers),
        CURLOPT_POSTFIELDS => json_encode($body),
    ]);
    curl_exec($ch);
    $code = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    return $code;
}

// Check both calls against the provider's current API docs before going live.
if (($cfg['provider'] ?? '') === 'beehiiv') {
    if (empty($cfg['beehiiv_api_key']) || empty($cfg['beehiiv_publication_id'])) done(503);
    $code = post_json(
        'https://api.beehiiv.com/v2/publications/' . rawurlencode($cfg['beehiiv_publication_id']) . '/subscriptions',
        ['Authorization: Bearer ' . $cfg['beehiiv_api_key']],
        ['email' => $email, 'reactivate_existing' => false, 'send_welcome_email' => true,
         'utm_source' => 'nasinthecut.com', 'utm_medium' => $source]
    );
} elseif (($cfg['provider'] ?? '') === 'kit') {
    if (empty($cfg['kit_api_key']) || empty($cfg['kit_form_id'])) done(503);
    $key = ['X-Kit-Api-Key: ' . $cfg['kit_api_key']];
    $code = post_json('https://api.kit.com/v4/subscribers', $key, ['email_address' => $email]);
    if ($code >= 200 && $code < 300) {
        $code = post_json('https://api.kit.com/v4/forms/' . rawurlencode($cfg['kit_form_id']) . '/subscribers', $key, ['email_address' => $email]);
    }
} else {
    done(503);
}

done($code >= 200 && $code < 300 ? 200 : 502);
