<?php
// Nas In The Cut: In The Cup seat requests.
// Stores each request privately in data/cup-requests.json. Read them on stats.php.

// Optional: an address to be emailed a short note for every new request. Leave empty to switch off.
const NOTIFY_EMAIL = '';

header('Cache-Control: no-store');
header('X-Robots-Tag: noindex');

$wantsJson = isset($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false;

function reply($ok, $message, $wantsJson, $code = 200) {
    if ($wantsJson) {
        http_response_code($code);
        header('Content-Type: application/json; charset=utf-8');
        echo json_encode(['ok' => $ok, 'message' => $message]);
    } else {
        header('Location: in-the-cup.html?seat=' . ($ok ? 'saved' : 'error') . '#seat', true, 303);
    }
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    reply(false, 'Use the form on the page.', $wantsJson, 405);
}

// Bots fill the hidden field. Tell them it worked and store nothing.
if (!empty($_POST['website'])) {
    reply(true, 'Saved.', $wantsJson);
}

$clean = function ($v, $max) {
    $v = trim(preg_replace('/\s+/u', ' ', (string) $v));
    return function_exists('mb_substr') ? mb_substr($v, 0, $max) : substr($v, 0, $max);
};
$name = $clean($_POST['name'] ?? '', 80);
$email = strtolower($clean($_POST['email'] ?? '', 120));
$mode = $_POST['mode'] ?? '';
$question = $clean($_POST['question'] ?? '', 400);
$oneToOne = ($_POST['one_to_one'] ?? '') === 'yes';

if ($name === '' || !filter_var($email, FILTER_VALIDATE_EMAIL) || !in_array($mode, ['in-person', 'online'], true)) {
    reply(false, 'Add your name, a valid email and how you will join.', $wantsJson, 400);
}

$dir = __DIR__ . '/data';
if (!is_dir($dir)) {
    @mkdir($dir, 0750, true);
}
$fp = fopen($dir . '/cup-requests.json', 'c+');
if (!$fp) {
    reply(false, 'That did not go through. Try again in a minute.', $wantsJson, 500);
}
flock($fp, LOCK_EX);
$list = json_decode(stream_get_contents($fp) ?: '[]', true);
if (!is_array($list)) {
    $list = [];
}

// Gentle limit: twenty requests a day from one connection (a shared cafe wifi still works).
// The address itself is never stored, only a one way fingerprint of it.
$who = hash('sha256', ($_SERVER['REMOTE_ADDR'] ?? '') . '|nitc-cup');
$recent = 0;
foreach ($list as $row) {
    if (($row['who'] ?? '') === $who && strtotime($row['at']) > time() - 86400) {
        $recent++;
    }
}
if ($recent >= 20) {
    flock($fp, LOCK_UN);
    fclose($fp);
    reply(false, 'You are already on the list. See you at the table.', $wantsJson, 429);
}

$entry = ['at' => gmdate('c'), 'name' => $name, 'email' => $email, 'mode' => $mode,
          'one_to_one' => $oneToOne, 'question' => $question, 'who' => $who];
$updated = false;
foreach ($list as $i => $row) {  // the same email updates its request instead of adding a new one
    if (($row['email'] ?? '') === $email) {
        $list[$i] = $entry;
        $updated = true;
        break;
    }
}
if (!$updated) {
    if (count($list) >= 5000) {
        flock($fp, LOCK_UN);
        fclose($fp);
        reply(false, 'The list is full right now. Message @nasinthecut on Instagram.', $wantsJson, 503);
    }
    $list[] = $entry;
}
ftruncate($fp, 0);
rewind($fp);
fwrite($fp, json_encode($list, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
fflush($fp);
flock($fp, LOCK_UN);
fclose($fp);

if (NOTIFY_EMAIL !== '' && !$updated) {
    @mail(NOTIFY_EMAIL, 'In The Cup: new seat request',
        "Name: $name\nEmail: $email\nJoining: $mode\nOne to one: " . ($oneToOne ? 'yes' : 'no') . "\nQuestion: $question\n",
        'From: In The Cup <no-reply@' . ($_SERVER['HTTP_HOST'] ?? 'nasinthecut.com') . '>');
}

reply(true, $updated ? 'Updated. You are on the list.' : 'You are on the list. Table details reach you first.', $wantsJson);
