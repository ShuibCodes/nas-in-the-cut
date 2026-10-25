<?php
// Nas In The Cut: private settings. NOT part of the website build.
// 1. Copy this file to nitc-config.php
// 2. Fill in the values
// 3. Upload it ONE LEVEL ABOVE public_html on Hostinger, for example
//    /home/u123456789/domains/nasinthecut.com/nitc-config.php
//    so it can never be opened from a browser.
return [
    // Which email provider the sign-up forms talk to: 'beehiiv' or 'kit'
    'provider' => 'beehiiv',

    // Beehiiv: Settings > API. Publication id starts with pub_
    'beehiiv_api_key' => '',
    'beehiiv_publication_id' => '',

    // Kit (ConvertKit): Settings > Developer > API key (v4), and the form id new readers join
    'kit_api_key' => '',
    'kit_form_id' => '',

    // Address that gets a note for each new In The Cup request (empty = off)
    'notify_email' => '',

    // Key for stats.php. Long and random. Change it if it is ever shared by mistake.
    'stats_key' => '',
];
